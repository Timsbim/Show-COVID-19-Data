from pathlib import Path
from datetime import date
import json


WORKING_DIR = 'MyDir'


# Basic structuring


def get_categories() -> list:
    # Providing the basic categories of data
    # - confirmed: Confirmed cases
    # - deaths: Deaths
    # - recovered: Recovered cases
    # - active: Active cases (confirmed - deaths - recovered)

    return ['confirmed', 'deaths', 'recovered', 'active']


def get_variants(category: str) -> list:
    variants = [
        'cum', 'cum_rel_popmio', 'cum_rel_pop100k',
        'diff', 'diff_rel_popmio', 'diff_rel_pop100k', 'diff_ma1w',
        'diff_rel_popmio_ma1w', 'diff_rel_pop100k_ma1w',
        'diff_rel_active'
    ]

    if category == 'active':
        return variants

    return variants[:-1]


# Web-related information


def get_feed_url(category: str) -> str:
    # Providing the data urls of JHU's github project (confirmed, deaths,
    # recovered)

    with get_settings_file_path('urls').open('r') as file:
        return json.load(file)[category]


# Paths and files


def get_dir_path(key: str, dte: date = None) -> Path:
    # Setting up the directory structure used in the rest of the application:
    # - base_path/settings: For settings (json-files with parameters)
    # - base_path/data/dte/feed: For the raw downloaded data
    # - base_path/data/dte: For the prepared data
    # - base_path/plots/dte: For the generated plots

    path = Path(WORKING_DIR)
    if key == 'settings':
        path = path / key
    elif key in ['base_data', 'base_plots']:
        path = path / key[5:]
    elif key in ['data', 'plots']:
        path = get_dir_path('base' + '_' + key) / dte.strftime('%y-%m-%d')
    elif key == 'feed':
        path = get_dir_path('data', dte) / key
    path.mkdir(parents=True, exist_ok=True)

    return path


def get_settings_file_path(key: str) -> Path:
    # Providing path to the settings files (json-files stored in the folder
    # ../settings, containing some basic parameters and definitions)

    return get_dir_path('settings').joinpath(key + '.json')


def get_feed_file_path(dte: date, category: str) -> Path:
    # Providing paths to the CSV-files used for saving the downloaded data:
    # dir_base/dte/data/feed_(confirmed/deaths/recovered).csv

    return get_dir_path('feed', dte).joinpath(category + '.csv')


def get_data_file_path(
        dte: date,
        name: str = 'data',
        file_format: str = 'json'
) -> Path:
    # Providing the path to the prepared csv/json-files from day dte
    # containing the data for category cat and variant var

    return get_dir_path('data', dte) / f"{name}.{file_format}"


def get_plot_file_path(dte: date, base: str, *args) -> Path:
    # Providing the path to the plot-file generated from day dte-data, defined
    # by the categories and variants specified in *args

    filename = base
    for arg in args:
        filename += '_' + arg
    filename += '.png'

    path = get_dir_path('plots', dte).joinpath(base)
    path.mkdir(parents=True, exist_ok=True)

    return path.joinpath(filename)


def get_region(region: str, subregion: str = '-') -> list:
    # Providing lists of countries organized in regions (e.g. Europe, middle,
    # south, east, north, ...). Definitions are stored in the settings file
    # regions.json in the folder ../settings.

    with get_settings_file_path('regions').open('r') as file:
        return json.load(file)[region][subregion]
