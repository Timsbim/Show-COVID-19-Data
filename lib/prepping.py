from urllib.request import urlopen
import pandas as pd

from lib.basics import *


# Retrieving data from github repository


def download_data() -> None:

    # Downloading the data from the JHU GitHub repository into feed files

    print_log('Downloading data from JHU repository ...')

    today = set_date()
    categories = ['base'] + get_categories()[:-1]

    for category in categories:
        # Establish access to data on the web
        response = urlopen(get_feed_url(category))

        # Read the data
        data = response.read().decode('utf-8')

        # Write data into the feed files
        with get_feed_file_path(today, category).open('w') as file:
            file.writelines(data)

    print_log('Download finished')

    return None


# Preparing data for further usage


def prepare_base_data(date_: str) -> None:

    # Preparing the basic data: How to name countries (ISO3, full name, and
    # population size)

    # Reading the feed csv-file into a DataFrame, taking only the necessary
    # columns (2 = ISO3-codes, 6 = province/state name, 7 = country name,
    # 11 = population size
    frame = pd.read_csv(str(get_feed_file_path(date_, 'base')),
                        usecols=[2, 6, 7, 11])

    # Dropping of:
    # - rows with 1. column (no ISO3-code) empty or 2. column
    #   ('Province_State') not empty (additional information on a sub-country
    #   level)
    # - column 2 (only used for filtering out unnecessary rows)
    drop_rows = [
        r for r in frame.index
        if pd.isna(frame.iat[r, 0]) or not pd.isna(frame.iat[r, 1])
    ]
    frame.drop(index=drop_rows, columns=[frame.columns[1]], inplace=True)

    # Dumping DataFrame in dictionary
    frame.columns = ['iso3', 'name', 'pop']
    countries = frame.to_dict(orient='records')
    countries += [
        {'iso3': 'DPR', 'name': 'Diamond Princess', 'pop': 3700},
        {'iso3': 'ZDM', 'name': 'MS Zaandam', 'pop': 1829},
        {'iso3': 'TTL', 'name': 'Total', 'pop': frame['pop'].sum(axis='index')}
    ]

    # Sorting alphabetically along iso3 code
    countries.sort(key=(lambda item: item['iso3']))

    # # Writing the table in the file data_base.csv in data folder of dte
    json.dump(countries,
              get_data_file_path(date_, name='base').open('w'),
              indent=4)

    return None


def get_base_data(date_: str,
                  columns: tuple = ('iso3', 'name', 'pop')
                  ) -> dict:

    # Extracting a (nested) dictionary from the base data from dte: The values
    # of the first column act as keys to the outer dictionary and the columns
    # as the keys of the inner dictionaries. If only 2 columns are request then
    # there's no inner dictionary: The values to the keys are the values of the
    # the 2. column.

    object_hook = (lambda obj: {column: obj[column] for column in columns})
    countries = json.load(get_data_file_path(date_, name='base').open('r'),
                          object_hook=object_hook)

    if len(columns) == 2:
        return {
            country[columns[0]]: country[columns[1]]
            for country in countries
        }

    key, *non_keys = columns
    return {
        country[key]: {column: country[column] for column in non_keys}
        for country in countries
    }


def prepare_data(date_: str, excel_output: bool = False) -> None:

    print_log('Preparing data ...')

    # Preparing the base data (name, keys, pop-numbers)
    prepare_base_data(date_)

    # Getting a dictionary that translates country names in iso3-code
    name_to_iso3 = get_base_data(date_, columns=('name', 'iso3'))

    categories = get_categories()
    prepped_data = {}
    for category in categories[:-1]:

        # Reading the csv-feed-file into a DataFrame
        frame = pd.read_csv(get_feed_file_path(date_, category))

        # Aggregate (sum) over rows which belong to the same country (names in
        # column 2), which also makes the country names the new index
        frame = frame.groupby(frame.columns[1]).sum()

        # Dropping the unnecessary columns (longitudes and latitudes -> 1, 2)
        frame.drop(columns=[frame.columns[i] for i in {0, 1}], inplace=True)

        # Setting a new index: ISO3-codes of the countries
        frame.index = pd.Index([name_to_iso3[name] for name in frame.index])

        # Transposing the DataFrame and thereby producing real time series
        frame = frame.T

        # Fixing index: Setting a new index with proper date-times
        frame.index = pd.Index(pd.to_datetime(list(frame.index)))

        # Fixing columns: Adding a column for the total sum of all countries
        frame = pd.concat([frame, frame.sum(axis='columns')], axis='columns')
        frame.rename({0: 'TTL'}, axis='columns', inplace=True)

        # Packing the frame in the dictionary for the prepped data
        prepped_data[category] = {'cum': frame.copy()}

    # Adding the table of cumulated data of active cases to the dictionary
    prepped_data['active'] = {}
    prepped_data['active']['cum'] = prepped_data['confirmed']['cum'] \
                                    - prepped_data['recovered']['cum'] \
                                    - prepped_data['deaths']['cum']

    # Creating the rest of the dependent data (rel, diffs, ma, ...)
    popn = get_base_data(date_, columns=('iso3', 'pop'))
    for category in categories:
        pmio = [
            popn[country] / 1e6
            for country in prepped_data[category]['cum'].columns
        ]
        p100k = [
            popn[country] / 1e5
            for country in prepped_data[category]['cum'].columns
        ]
        prepped_data[category]['cum_rel_popmio'] = \
            prepped_data[category]['cum'].div(pmio)
        prepped_data[category]['cum_rel_pop100k'] = \
            prepped_data[category]['cum'].div(p100k)
        prepped_data[category]['diff'] = \
            prepped_data[category]['cum'].diff()
        prepped_data[category]['diff_rel_popmio'] = \
            prepped_data[category]['cum_rel_popmio'].diff()
        prepped_data[category]['diff_rel_pop100k'] = \
            prepped_data[category]['cum_rel_pop100k'].diff()
        prepped_data[category]['diff_ma1w'] = \
            prepped_data[category]['diff'].rolling(7).mean()
        prepped_data[category]['diff_rel_popmio_ma1w'] = \
            prepped_data[category]['diff_rel_popmio'].rolling(7).mean()
        prepped_data[category]['diff_rel_pop100k_ma1w'] = \
            prepped_data[category]['diff_rel_pop100k'].rolling(7).mean()
        if category == 'active':
            prepped_data[category]['diff_rel_active'] = \
                prepped_data[category]['diff'].div( \
                    prepped_data[category]['cum'].shift(periods=1))

    # If asked for (keyword argument excel_output=True): Writing the data
    # organised by tables which respectively contain all countries sheet-wise
    # into one large Excel-file
    if excel_output:

        print_log('Writing Excel-file ...')

        xlsx_file_path = str(get_data_file_path(date_, file_format='xlsx'))
        with pd.ExcelWriter(xlsx_file_path) as xlsx_file:
            for category, variant in [
                                        (category, variant)
                                        for category in categories
                                        for variant in prepped_data[category]
                                     ]:
                frame = prepped_data[category][variant]
                frame.to_excel(xlsx_file, sheet_name=f"{category}_{variant}")

        print_log('Excel-file finished')

    # Writing the data in one JSON-file: Organized with a multi-index
    # (category, variant, day) and the countries as columns

    # Stacking the individual frames in order category -> variant after
    # adjusting the index
    frame_all = pd.DataFrame()
    for category, variant in [
                                (category, variant)
                                for category in categories
                                for variant in prepped_data[category]
                             ]:
        frame = prepped_data[category][variant]
        frame.index = \
            pd.MultiIndex.from_tuples(zip([category] * len(frame.index),
                                          [variant] * len(frame.index),
                                          list(frame.index)))
        frame_all = pd.concat([frame_all, frame])

    # Giving the new index names, and the columns as well
    frame_all.index.names = ['category', 'variant', 'date']
    frame_all.columns.name = 'country'

    # Sorting for better query performance
    frame_all.sort_index()

    # Writing the new frame in a JSON-file

    print_log('Writing JSON-file ...')

    json_file_path = get_data_file_path(date_, file_format='json.gz')
    frame_all.to_json(json_file_path,
                      orient='table',
                      indent=4,
                      compression='gzip')

    print_log('JSON-file finished')

    print_log('Data preparation finished')

    return None
