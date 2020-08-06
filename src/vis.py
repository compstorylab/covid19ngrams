
from __future__ import unicode_literals
import numpy as np
import pandas as pd
import datetime

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.lines import Line2D
import matplotlib.ticker as ticker

import consts
from query import Query

import warnings
warnings.simplefilter("ignore")

import logging
logger = logging.getLogger(__name__)


def cases(
    savepath,
    words_by_country,
    deaths,
    confirmed,
    us_deaths,
    us_confirmed,
    lang_hashtbl,
):
    """ Plot a grid of case-counts and ngrams

    Args:
        savepath (pathlib.Path): path to save generated plot
        words_by_country (dict): a dictionary of ngrams by country
        deaths (pathlib.Path): path to death records by JHU
        confirmed (pathlib.Path): path to case counts by JHU
        us_deaths (pathlib.Path): path to death records by JHU for the US
        us_confirmed (pathlib.Path): path to case counts by JHU for the US
        words (list): a list of tuples ('ngram', 'isocode')
        lang_hashtbl (pathlib.Path): path to parse requested languages
    """
    us_deaths = pd.read_csv(
        us_deaths, header=0
    ).groupby(by=['Country_Region']).sum().drop(
        ['UID', 'code3', 'FIPS', 'Lat', 'Long_', 'Population'],
        axis=1
    ).T

    deaths = pd.read_csv(
        deaths, header=0
    ).groupby(by=['Country/Region']).sum().drop(['Lat', 'Long'], axis=1).T
    deaths['United States'] = us_deaths
    deaths.index = pd.to_datetime(deaths.index)
    deaths = deaths.diff(periods=1)

    us_confirmed = pd.read_csv(
        us_confirmed, header=0
    ).groupby(by=['Country_Region']).sum().drop(
        ['UID', 'code3', 'FIPS', 'Lat', 'Long_'],
        axis=1
    ).T

    confirmed = pd.read_csv(
        confirmed, header=0
    ).groupby(by=['Country/Region']).sum().drop(['Lat', 'Long'], axis=1).T
    confirmed['United States'] = us_confirmed
    confirmed.index = pd.to_datetime(confirmed.index)
    confirmed = confirmed.diff(periods=1)

    ngrams = {c: [] for c in consts.countries}
    supported_languages = pd.read_csv(lang_hashtbl, header=0, index_col=1, comment='#')

    for country, words in words_by_country.items():
        for w, lang in words:
            n = len(w.split())
            logger.info(f"Retrieving {supported_languages.loc[lang].Language}: {n}gram -- '{w}'")

            q = Query(f'{n}grams', lang)
            d = q.query_timeseries(w, start_time=datetime.datetime(2020, 1, 1))

            logger.info(f"Top rank: {d['rank'].min()} -- {d['rank'].idxmin().date()}")
            d.index.name = f"{supported_languages.loc[lang].Language}\n'{w}'"
            d.index.name = f"{supported_languages.loc[lang].Language}\n'{w}'"
            ngrams[country].append(d)

    plot_cases(savepath, ngrams, deaths, confirmed)
    logger.info(f'Saved: {savepath}')


def plot_cases(savepath, ngrams, deaths, confirmed):
    """Plot a grid of contagiograms

    Args:
        savepath (pathlib.Path): path to save plot
        ngrams (dict): a dictionary of ngrams by country
        deaths (pd.DataFrame): a dataframe of death records by JHU
        confirmed (pd.DataFrame): a dataframe of case counts by JHU
    """
    plt.rcParams.update({
        'font.size': 10,
        'axes.titlesize': 14,
        'axes.labelsize': 12,
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,
        'legend.fontsize': 10,
    })

    rows, cols = 16, 3
    fig = plt.figure(figsize=(12, 14))
    gs = fig.add_gridspec(ncols=cols, nrows=rows)

    minr, maxr = 1, 10 ** 5
    minc, maxc = 1, 10 ** 5
    major_locator = mdates.YearLocator()
    major_format = '%b\n%Y'
    minor_format = '%b'
    minor_locator = mdates.AutoDateLocator()
    start_date = datetime.datetime(2020, 1, 1)
    end_date = datetime.datetime.today()-datetime.timedelta(days=2)
    window_size = 7

    i = 0
    for r in np.arange(0, rows, step=4):
        for c in np.arange(cols):

            ax = fig.add_subplot(gs[r:r+3, c])
            tax = ax.twinx()

            ax.set_title(consts.countries[i], fontsize=14)

            ax.annotate(
                consts.tags[i], xy=(-.1, 1.1), color='k', weight='bold',
                xycoords="axes fraction", fontsize=16,
            )

            tss = []
            for w in ngrams[consts.countries[i]]:
                w = w[:-2]
                w.index = pd.to_datetime(w.index)
                w['rank'] = w['rank'].fillna(maxr)
                tss.append(w['rank'])

                ax.plot(
                    w['rank'].rolling(window_size, center=True).mean(),
                    color='grey',
                    alpha=.3
                )

            tss = pd.DataFrame(tss).mean(axis=0)
            ax.plot(
                tss.rolling(window_size, center=True).mean(),
                color='k',
            )

            tax.plot(
                confirmed[consts.countries[i]].rolling(window_size, center=True).mean(),
                color='red'
            )

            tax.plot(
                deaths[consts.countries[i]].rolling(window_size, center=True).mean(),
                color='C1',
                ls='--'
            )

            ax.set_xlim(start_date, end_date)
            ax.xaxis.set_major_locator(major_locator)
            ax.xaxis.set_major_formatter(mdates.DateFormatter(major_format))
            ax.xaxis.set_minor_locator(minor_locator)
            ax.xaxis.set_minor_formatter(mdates.DateFormatter(minor_format))

            ax.set_ylim(minr, maxr)
            ax.invert_yaxis()
            ax.set_yscale('log')
            ax.yaxis.set_major_locator(
                ticker.LogLocator(base=10, numticks=12)
            )
            ax.set_yticks(
                [10**i for i in range(6)],
                minor=False
            )
            ax.set_yticklabels(
                ['1', '10', '100', r'$10^3$', r'$10^4$', r'$10^5$'],
                minor=False,
            )
            ax.yaxis.set_minor_locator(
                ticker.LogLocator(base=10.0, subs=np.arange(.1, 1, step=.1), numticks=30)
            )

            tax.spines['right'].set_color('red')
            tax.tick_params(axis='y', which='both', colors='red', labelcolor='red')
            tax.yaxis.label.set_color('red')

            tax.set_xlim(start_date, end_date)
            tax.xaxis.set_major_locator(major_locator)
            tax.xaxis.set_major_formatter(mdates.DateFormatter(major_format))
            tax.xaxis.set_minor_locator(minor_locator)
            tax.xaxis.set_minor_formatter(mdates.DateFormatter(minor_format))

            tax.set_ylim(minc, maxc)
            tax.set_yscale('log')
            tax.yaxis.set_major_locator(
                ticker.LogLocator(base=10, numticks=12)
            )
            tax.set_yticks(
                [10**i for i in range(6)],
                minor=False
            )
            tax.set_yticklabels(
                ['1', '10', '100', r'$10^3$', r'$10^4$', r'$10^5$'],
                minor=False,
            )
            tax.yaxis.set_minor_locator(
                ticker.LogLocator(base=10.0, subs=np.arange(.1, 1, step=.1), numticks=30)
            )

            tax.grid(True, which="major", axis='y', alpha=.3, lw=1, linestyle='-', color='C0')

            if c == 0:
                ax.text(
                    -0.25, 0.5, "Average\n"+r"$n$-gram"+"\nrank\n"+r"$\langle r \rangle$", ha='center',
                    verticalalignment='center', transform=ax.transAxes,
                )

                ax.text(
                    -0.25, 0.15, "Less\nTalked\nAbout\n↓", ha='center',
                    verticalalignment='center', transform=ax.transAxes, color='grey'
                )
                ax.text(
                    -0.25, 0.85, "↑\nMore\nTalked\n About", ha='center',
                    verticalalignment='center', transform=ax.transAxes, color='grey'
                )

                if r == 0:
                    ax.legend(
                        handles=[
                            Line2D([0], [0], lw=2, color='grey', label=r'Salient $n$-gram'),
                            Line2D([0], [0], color='r', lw=2, label='Reported cases'),
                            Line2D([0], [0], color='C1', ls='--', lw=2, label='Reported Deaths'),
                        ],
                        loc='lower right',
                        ncol=1,
                        frameon=False,
                        fontsize=11,
                    )
            else:
                ax.set_yticklabels([])

            if c == 2:
                tax.set_ylabel(
                    f"Number of new cases/deaths",
                    color='red'
                )
            else:
                tax.set_yticklabels([])

            if c == cols - 1 and r == 0:
                ax.text(
                    .88, 1.15,
                    f"Last updated\n{end_date.strftime('%Y/%m/%d')}",
                    ha='center',
                    verticalalignment='center', transform=ax.transAxes
                )

            i += 1

    plt.subplots_adjust(top=0.97, right=0.97, hspace=0.2, wspace=.15)
    plt.savefig(f'{savepath}.pdf', bbox_inches='tight', pad_inches=.25)
    plt.savefig(f'{savepath}.png', dpi=300, bbox_inches='tight', pad_inches=.25)

