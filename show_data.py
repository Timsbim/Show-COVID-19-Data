from datetime import date

from lib.basics import get_region
from lib.prepping import download_data, prepare_data
from lib.showing import show_countries, show_groups


if __name__ == '__main__':
    # Data are renewed daily (normally between midnight and the early morning
    # hours). Setting the day decides which data are going to be processed. Be
    # careful: Downloaded data have to be available for the selected day for
    # the functions:
    # - prepare_data
    # - show_countries
    # - show_groups

    # Setting the date
    today = date.today()

    # Downloading data
    download_data()

    # Preparing data
    prepare_data(today)

    # Plotting single countries
    length = 175
    # show_countries(today, 'TTL', length=length)
    show_countries(today, *get_region('europe', 'west'), length=length)
    show_countries(today, *get_region('europe', 'north'), length=length)
    show_countries(today, *get_region('europe', 'south'), length=length)
    show_countries(today, *get_region('europe', 'east'), length=length)
    show_countries(today, *get_region('europe', 'balkans'), length=length)
    # show_countries(today, *get_region('america', 'north'), length=length)
    # show_countries(today, *get_region('america', 'south'), length=length)
    # show_countries(today, *get_region('africa', 'south'), length=length)

    # Plotting groups of countries
    show_groups(today, {'DEU vs. BiH': ['BIH', 'DEU']}, length=length)
    # show_groups(today, {'DEU vs. ROU': ['ROU', 'DEU']}, length=length)
    show_groups(today, {'DEU vs. SWE': ['SWE', 'DEU']}, length=length)
    show_groups(today, {'DEU vs. ITA': ['ITA', 'DEU']}, length=length)
    show_groups(today, {'DEU vs. FRA': ['FRA', 'DEU']}, length=length)
    # show_groups(today, {'DEU vs. USA': ['USA', 'DEU']}, length=length)
