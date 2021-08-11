import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from lib.basics import *
from lib.prepping import get_base_data


# Showing the data


def get_country_data_to_show(date_, plots, *countries, length=1000):
    """Returns the data from day date_ for the categories and variants defined
    in the dictionary plots and the countries, all loaded in one dictionary
    """
    tbl = pd.read_json(
        get_data_file_path(date_, file_format="json.gz"),
        orient="table",
        compression="gzip",
    ).sort_index()

    data = dict()
    for country in countries:
        data[country] = {category: {} for category in plots}
    for category, variant, country in [
        (category, variant, country)
        for category in plots
        for variant in plots[category]
        for country in countries
    ]:
        data[country][category][variant] = tbl.loc[
            (category, variant), country
        ].tail(length)

    return data


def get_title_translation():
    """Returns dictionary which translates shortcuts in text suitable for plot
    titles
    """
    return json.load(get_settings_file_path("title_translation").open("r"))


def setup_ax(ax, days):
    """Set up the axes for the plots"""

    # Months
    months = (
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    )

    # Setting the viewable range of x-axis
    ax.set_xlim(-2, len(days) + 1)

    # Setting the ticks (positions and labels) mostly on x-axis

    # Minor ticks: Only 3 for each month, roughly the end of the 1., 2. and 3.
    # week
    minor_ticks = [i for i in range(len(days)) if days[i].day in (8, 16, 24)]

    # Minor labels: Day of minor tick, i.e. 8, 16 and 24
    minor_labels = [days[i].day for i in minor_ticks]

    # Major: Ticks = months end/beginning, label: short version of months name
    major_ticks = []
    major_labels = []
    month = days[0].month
    for i, day in enumerate(days[1:], start=1):
        # Detecting the beginning of a new month
        if day.month != month:
            major_ticks.append(i)
            month = day.month
            major_labels.append(months[month - 1])

    # Actually setting the prepared ticks/labels, including the label size
    ax.xaxis.set_ticks(minor_ticks, minor=True)
    ax.xaxis.set_ticklabels(minor_labels, minor=True)
    ax.xaxis.set_ticks(major_ticks, minor=False)
    ax.xaxis.set_ticklabels(major_labels, minor=False)
    ax.xaxis.set_tick_params(which="both", labelsize=14)
    ax.yaxis.set_tick_params(which="both", labelsize=14)

    # Setting the grid
    ax.grid(True, which="both")
    ax.grid(which="major", linestyle="dashed", linewidth=2)
    ax.grid(which="minor", linestyle="dashed")

    # Setting the labels of the x-axis, including the font size
    ax.set_xlabel("day", fontsize=16)


def show_countries(date_: str, *countries: str, length: int = 1000) -> None:
    """Creates a standard set of plots for every country provided by the
    argument countries (usually a list). The set contains:
    - Confirmed cases, cumulative and diffs (including the 1-week-moving
      average)
    - Deaths, cumulative and diffs (including the 1-week-moving average)
    - Active cases, cumulative and diffs (including the 1-week-moving
      average)
    The plots are available in single-plot files, files per category
    (containing 2 plots), and a file containing all 6 plots
    """
    print_log(f"Plotting countries: {str.join(', ', countries)} ...")

    # Defining the plots that should be included
    plots = {
        "confirmed": ["cum", "diff", "diff_ma1w"],
        "deaths": ["cum", "diff", "diff_ma1w"],
        "active": ["cum", "diff", "diff_ma1w"],
    }
    categories = plots

    # Getting the title text bits
    trsl = get_title_translation()
    iso3_to_name = get_base_data(date_, columns=("iso3", "name"))

    # Read data from files produced by prepare_data
    data = get_country_data_to_show(date_, plots, *countries, length=length)

    # Creating the plots for the selected countries
    title_font_size = 30
    for country in countries:
        # Creating the figure which includes all plots
        fig_all, axs_all = plt.subplots(3, 2, figsize=(40, 50))
        fig_all.suptitle(
            iso3_to_name[country], fontsize=title_font_size, fontweight="bold"
        )

        for i, category in enumerate(categories):
            # Creating the figure for all plots per category
            fig_cat, axs_cat = plt.subplots(2, 1, figsize=(20, 25))
            fig_cat.suptitle(
                f"{iso3_to_name[country]} - {trsl[category]}",
                fontsize=title_font_size,
                fontweight="bold",
            )

            for j, variant in enumerate(["cum", "diff"]):
                series = data[country][category][variant]
                days = list(series.index)

                # Creating the figure for single plot (category and variant)
                fig, axs = plt.subplots(figsize=(25, 16))
                fig.suptitle(
                    f"{iso3_to_name[country]} - "
                    f"{trsl[category]} - {trsl[variant]}",
                    fontsize=title_font_size,
                    fontweight="bold",
                )
                for ax in [axs, axs_cat[j], axs_all[i][j]]:
                    ax.set_title(
                        f"{trsl[category]} - {trsl[variant]}", fontsize=20
                    )
                    setup_ax(ax, days)
                    ax.plot(
                        list(range(len(series.index))), series.values, "bo"
                    )
                    if variant == "diff":
                        series_ma = data[country][category]["diff_ma1w"]
                        ax.plot(
                            list(range(len(series_ma.index))),
                            series_ma.values,
                            "r-",
                            label=trsl["diff_ma1w"],
                        )
                        ax.legend(fontsize="xx-large")

                    # Due to data corrections there are sometimes negative
                    # diffs for confirmed cases, which should be always
                    # non-negative. This can lead to distorted plots and is
                    # therefore adjusted by setting the minimum value of the
                    # y-axis to -25.
                    if category == "confirmed" and variant == "diff":
                        ax.set_ylim(bottom=-25)

                # Saving the figure for single plot
                fig.align_labels()
                fig.savefig(
                    get_plot_file_path(date_, country, category, variant)
                )

            # Saving the figure with all plots per category
            fig_cat.align_labels()
            fig_cat.savefig(get_plot_file_path(date_, country, category))

        # Saving the figure with all plots
        fig_all.align_labels()
        fig_all.savefig(get_plot_file_path(date_, country))

        plt.close("all")

        print_log(f"Plots for {country} finished")

    print_log("Plotting finished")


def get_group_data_to_show(date_, plots, groups, length=1000):
    """Returns the data from day dte for the categories and variants defined
    in the dictionary plots and the groups in list groups, loaded into a
    dictionary
    """
    tbl = pd.read_json(
        get_data_file_path(date_, file_format="json.gz"),
        orient="table",
        compression="gzip",
    ).sort_index()

    data = dict()
    for group in groups:
        data[group] = {category: {} for category in plots}
    for category, variant, group in [
        (category, variant, group)
        for category in plots
        for variant in plots[category]
        for group in groups
    ]:
        data[group][category][variant] = tbl.loc[
            (category, variant), groups[group]
        ].tail(length)

    return data


def show_groups(date_: str, groups: dict, length: int = 1000) -> None:
    """Creates a standard set of plots for groups of countries provided by the
    argument groups (a dictionary). The set contains:
    - Confirmed cases per million, cumulative and diffs (including the
      1-week-moving average)
    - Deaths per 100,000, cumulative and diffs (including the 1-week-moving
      average)
    - Active cases per million, cumulative and diffs (including the
      1-week-moving average)
    The plots are available in single-plot files, files per category
    (containing 2 plots), and a file containing all 6 plots
    """
    # Defining the plots that should be included
    plots = {
        "confirmed": ["cum_rel_popmio", "diff_rel_popmio_ma1w"],
        "deaths": ["cum_rel_pop100k", "diff_rel_pop100k_ma1w"],
        "active": ["cum_rel_popmio", "diff_rel_popmio_ma1w"],
    }
    trsl = get_title_translation()
    categories = plots

    # Reading data from files produced by prepare_data
    data = get_group_data_to_show(date_, plots, groups, length)

    title_font_size = 30
    for group in groups:
        print_log(
            f"Plotting group {group} with countries "
            f"{str.join(', ', groups[group])} ..."
        )

        # Creating list of countries in group
        countries = groups[group]

        # Creating the figure which includes all plots
        fig_all, axs_all = plt.subplots(3, 2, figsize=(40, 50))
        fig_all.suptitle(group, fontsize=title_font_size, fontweight="bold")
        for i, category in enumerate(categories):
            variants = plots[category]

            # Creating the figure for all plots per category
            fig_cat, axs_cat = plt.subplots(2, 1, figsize=(20, 25))
            fig_cat.suptitle(
                f"{group} - {trsl[category]}",
                fontsize=title_font_size,
                fontweight="bold",
            )
            for j, variant in enumerate(variants):
                # Creating the figure for single plot (category and variant)
                fig, axs = plt.subplots(figsize=(25, 16))
                fig.suptitle(
                    f"{group} - {trsl[category]} - {trsl[variant]}",
                    fontsize=title_font_size,
                    fontweight="bold",
                )
                for ax in [axs, axs_cat[j], axs_all[i][j]]:
                    ax.set_title(
                        f"{trsl[category]} - {trsl[variant]}", fontsize=20
                    )
                    days = list(data[group][category][variant].index)
                    setup_ax(ax, days)
                    ax.plot(
                        list(range(len(days))),
                        data[group][category][variant][countries],
                        "o",
                    )
                    ax.legend(countries)

                    # Due to data corrections there are sometimes negative
                    # diffs for confirmed cases, which should be always
                    # non-negative. This can lead to distorted plots and is
                    # therefore adjusted by setting the minimum value of the
                    # y-axis to -10.
                    if (
                        category == "confirmed"
                        and variant == "diff_rel_popmio_ma1w"
                    ):
                        ax.set_ylim(bottom=-10)

                # Saving the figure with single plot
                fig.align_labels()
                fig.savefig(
                    get_plot_file_path(date_, group, category, variant)
                )

                # Saving the figure with all plots per category
            fig_cat.align_labels()
            fig_cat.savefig(get_plot_file_path(date_, group, category))

        # Saving the figure with all plots
        fig_all.align_labels()
        fig_all.savefig(get_plot_file_path(date_, group))
        plt.close("all")

        print_log("Plotting finished")


def show_countries_beyond_threshold(
    date_, category, variant, threshold, *countries
):
    """Creates a plot for the variable category -> variant for the group of
    countries. Here the plots are "normalized": The series starts with the
    day the variable first exceeds the threshold. I.e., the x-axis just
    shows the number of days (past exceeding the threshold), not calendar
    days.
    """
    # Fetching the relevant data and loading it into a DataFrame
    plots = {category: [variant]}
    data = get_country_data_to_show(date_, plots, *countries)
    tbl = pd.DataFrame()
    for country in countries:
        tbl.insert(
            loc=len(tbl.columns),
            column=country,
            value=data[country][category][variant],
        )

    # Initializing the plot
    fig, ax = plt.subplots(figsize=(20, 7.5))

    # Processing the series into the plot
    for country in tbl.columns:
        series = tbl[country]
        series.index = np.arange(len(series.index))
        try:
            # Adjust the series: New series starts with the first day it
            # exceeds the threshold
            start = series[series > threshold].index[0]
            series_new = pd.Series(series[start:].values)
            series_new.name = series.name
            # Adding new series to plot
            ax.plot(series_new, ".")
        finally:
            # If all values of the series are below the threshold the series
            # isn't included in the plot (obviously)
            pass

    # Setting up the plot
    ax.grid(which="major", linestyle="dashed", linewidth=1)
    trsl = get_title_translation()
    ax.set_title(
        f"{trsl[category]} - {trsl[variant]}: "
        f"Days beyond threshold ({threshold})"
    )
    ax.set_xlabel(f"days")
    ax.set_ylabel(f"{category}")
    ax.legend(countries)
    plt.show()
    plt.close("all")
