from argparse import ArgumentParser
from utils import *


def get_arguments():
    parser = ArgumentParser(
        prog="Show Covid-19",
        description="Make charts of Covid-19 data",
    )
    parser.add_argument(
        "-n", "--no-download",
        help="no new data download",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "countries",
        help="specify countries by iso code, e.g. DEU for Germany",
        nargs="*",
    )
    parser.add_argument(
        "-g", "--groups",
        help="specify comparison groups, e.g. DEU-FRA for Germany vs. France",
        nargs="*",
    )
    parser.add_argument(
        "-l", "--length",
        help="specify length of time series in days (default is 365 days)",
        type=int,
        default=365,
    )
    return parser.parse_args()


if __name__ == "__main__":
    
    # Evaluate the arguments
    args = get_arguments()
    countries = args.countries
    download = not args.no_download
    groups = args.groups
    length = args.length
    
    # Setting the date
    today = set_date()

    if download:
        # Downloading data
        download_data()

        # Preparing data
        prepare_data(today)

    # show_countries(today, 'TTL', length=length)
    if len(countries) > 0:
        show_countries(today, *countries, length=length)
    
    # Plotting groups of countries
    if groups is not None:
        groups = {
            " vs. ".join(group.split("-")): group.split("-")
            for group in groups
        }
        show_groups(today, groups, length=length)
 
