import datetime as dt
import json
from pathlib import Path
from sys import argv
from time import strftime


# Logging (console)


def print_log(message):
    """Simple logging function: Adds timestamp before message"""
    print(strftime("%H:%M:%S") + ": " + message)


# Basic structures


def set_date(date=None):
    """Provides the processing date"""
    if not date:
        return dt.date.today().strftime("%y-%m-%d")
    else:
        return date


def get_categories():
    """Provides the basic categories of data
    - confirmed: Confirmed cases
    - deaths: Deaths
    - recovered: Recovered cases
    - active: Active cases (confirmed - deaths - recovered)
    """
    return ["confirmed", "deaths", "recovered", "active"]


def get_variants(category):
    """Provides the different data variants"""
    variants = [
        "cum",
        "cum_rel_popmio",
        "cum_rel_pop100k",
        "diff",
        "diff_rel_popmio",
        "diff_rel_pop100k",
        "diff_ma1w",
        "diff_rel_popmio_ma1w",
        "diff_rel_pop100k_ma1w",
        "diff_rel_active",
    ]
    if category == "active":
        return variants
    return variants[:-1]


# Web-related information


def get_feed_url(category):
    """Provides the data urls of John Hopkins University's GitHub project
    (confirmed, deaths, recovered)
    """
    with get_settings_file_path("urls").open("r") as file:
        return json.load(file)[category]


# Paths and files


def get_dir_path(key, date=None):
    """Sets up the directory structure used in the rest of the application:
    - script_path/settings: For settings (json-files with parameters)
    - output_path/data/dte/feed: For the raw downloaded data
    - output_path/data/dte: For the prepared data
    - output_path/plots/dte: For the generated plots
    """
    # Determine settings directory: Subdirectory of the directory in which the
    # script is located, named "settings"
    if key == "settings":
        return Path(argv[0]).parent / key

    # Determine the output directory: Either stored in the "output_dir.json"-
    # file located in the settings directory or the directory in which the
    # script is located
    path = Path(argv[0]).parent
    if get_settings_file_path("output_dir").exists():
        with get_settings_file_path("output_dir").open("r") as file:
            settings = json.load(file)
        if settings["OUTPUT_DIR"] != "":
            path = Path(settings["OUTPUT_DIR"])

    # Output directories
    if key in ["base_data", "base_plots"]:
        path = path / key[5:]
    elif key in ["data", "plots"]:
        path = get_dir_path("base" + "_" + key) / date
    elif key == "feed":
        path = get_dir_path("data", date) / key
    path.mkdir(parents=True, exist_ok=True)

    return path


def get_settings_file_path(key):
    """Provides path to the settings files (json-files stored in the folder
    ../settings, containing some basic parameters and definitions)
    """
    return get_dir_path("settings").joinpath(key + ".json")


def get_feed_file_path(date, category):
    """Provides paths to the CSV-files used for saving the downloaded data:
    dir_base/dte/data/feed_(confirmed/deaths/recovered).csv
    """
    return get_dir_path("feed", date).joinpath(category + ".csv")


def get_data_file_path(date, name="data", file_format="json"):
    """Provides the path to the prepared csv/json-files from day dte
    containing the data for category cat and variant var
    """
    return get_dir_path("data", date) / f"{name}.{file_format}"


def get_plot_file_path(date, base, *args):
    """Provides the path to the plot-file generated from day dte-data, defined
    by the categories and variants specified in *args
    """
    filename = base
    for arg in args:
        filename += "_" + arg
    filename += ".png"

    path = get_dir_path("plots", date).joinpath(base)
    path.mkdir(parents=True, exist_ok=True)

    return path.joinpath(filename)


def get_region(region, subregion="-"):
    """Provides lists of countries organized in regions (e.g. Europe, middle,
    south, east, north, ...). Definitions are stored in the settings file
    regions.json in the folder ../settings.
    """
    with get_settings_file_path("regions").open("r") as file:
        return json.load(file)[region][subregion]
