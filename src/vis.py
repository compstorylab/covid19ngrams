
from __future__ import unicode_literals
import numpy as np
import pandas as pd
import datetime
from query import Query

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.lines import Line2D
from bidi import algorithm as bidialg
import matplotlib.ticker as ticker

import consts

import warnings
warnings.simplefilter("ignore")


def contagiograms(
        savepath,
        words,
        lang_hashtbl,
        start_date=datetime.datetime(2019, 12, 1)
):
    """ Plot a grid of contagiograms

    Args:
        savepath (pathlib.Path): path to save generated plot
        words (list): a list of tuples ('ngram', 'isocode')
        lang_hashtbl (pathlib.Path): path to parse requested languages
        case_sensitive (bool): a toggle for case_sensitive lookups
        start_date (datetime): starting date for the query
    """
    ngrams = []
    supported_languages = pd.read_csv(lang_hashtbl, header=0, index_col=1, comment='#')

    for i, (w, lang) in enumerate(words[:12]):
        n = len(w.split())
        print(f"Retrieving {supported_languages.loc[lang].Language}: {n}gram -- '{w}'")

        q = Query(f'{n}grams', lang)
        d = q.query_timeseries(w, start_time=start_date)

        print(f"Top rank: {d['rank'].min()} -- {d['rank'].idxmin().date()}")
        d.index.name = f"{supported_languages.loc[lang].Language}\n'{w}'"
        d.index.name = f"{supported_languages.loc[lang].Language}\n'{w}'"
        ngrams.append(d)

    plot_contagiograms(savepath, ngrams, metric='rank')
    print(f'Saved: {savepath}')


def cases(
    savepath,
    deaths,
    confirmed,
    us_deaths,
    us_confirmed,
    lang_hashtbl,
):
    """ Plot a grid of case-counts and ngrams

    Args:
        savepath (pathlib.Path): path to save generated plot
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

    plot_cases(savepath, deaths, confirmed)
    print(f'Saved: {savepath}')


def plot_contagiograms(savepath, ngrams, rolling_avg=True, metric='rank'):
    """Plot a grid of contagiograms

    Args:
        savepath (pathlib.Path): path to save plot
        ngrams (list[tuple]): a 2D-list of ngrams to plot
        rolling_avg (bool): a toggle for plotting a rolling average of the timeseries
        metric (string): plot either rate of usage (freq) or rank of work (rank)
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
    window_size = 7
    legend = True

    major_locator = mdates.YearLocator()
    major_format = '%b\n%Y'
    minor_format = '%b'
    minor_locator = mdates.AutoDateLocator()
    contagion_resolution = 'D'

    if metric == 'rank':
        vmin, vmax = 0, 6
    else:
        vmin, vmax = -6, -1

    i = 0
    for r in np.arange(0, rows, step=4):
        for c in np.arange(cols):

            ax = fig.add_subplot(gs[r + 1:r + 3, c])
            cax = fig.add_subplot(gs[r, c])

            df = ngrams[i]
            df.index = pd.to_datetime(df.index)

            start_date = df.index[0]
            end_date = df.index[-1]
            ax.set_xlim(start_date, end_date)
            cax.set_xlim(start_date, end_date)

            ax.xaxis.set_major_locator(major_locator)
            ax.xaxis.set_major_formatter(mdates.DateFormatter(major_format))
            ax.xaxis.set_minor_locator(minor_locator)
            ax.xaxis.set_minor_formatter(mdates.DateFormatter(minor_format))

            cax.xaxis.set_major_locator(major_locator)
            cax.xaxis.set_major_formatter(mdates.DateFormatter(major_format))
            cax.xaxis.set_minor_locator(minor_locator)
            cax.xaxis.set_minor_formatter(mdates.DateFormatter(minor_format))

            df.dropna(inplace=True)
            df['freq'] = df['freq'].apply(np.log10)
            df['freq_no_rt'] = df['freq_no_rt'].apply(np.log10)

            df['rank'] = df['rank'].apply(np.log10)
            df['rank_no_rt'] = df['rank_no_rt'].apply(np.log10)

            at = df['count'].resample(contagion_resolution).mean()
            ot = df['count_no_rt'].resample(contagion_resolution).mean()
            rt = at - ot

            cax.annotate(
                consts.tags[i], xy=(-.16, 1.2), color='k', weight='bold',
                xycoords="axes fraction", fontsize=16,
            )

            lang, word = df.index.name.split('\n')
            try:
                word = bidialg.get_display(word)
            except UnicodeEncodeError:
                word = str(word, 'utf-8')

            if not word.isascii() and lang in consts.fonts.keys():
                prop = consts.fonts.get(lang)
            else:
                prop = consts.fonts.get('Default')

            cax.text(
                .5,
                1.75,
                lang,
                horizontalalignment='center',
                verticalalignment='top',
                transform=cax.transAxes,
                fontsize=14,
                color='grey'
            )
            cax.text(
                .5,
                1.4,
                word,
                horizontalalignment='center',
                verticalalignment='top',
                fontproperties=prop,
                transform=cax.transAxes,
                fontsize=14,
            )


            try:
                # plot contagion fraction
                try:
                    idx = np.argwhere((rt - ot) > 0).flatten()
                    if len(idx) > 0:
                        for d in rt[idx].index:
                            cax.axvline(d, color='orangered', alpha=.1)

                except IndexError:
                    pass

                cax.plot(
                    ot / at,
                    lw=1,
                    color=consts.ot_color
                )
                cax.plot(
                    rt / at,
                    lw=1,
                    color=consts.rt_color
                )

                # plot timeseries
                ax.plot(
                    df[metric],
                    marker='o',
                    ms=3,
                    color='grey',
                    mfc='grey',
                    mec='grey',
                    lw=0,
                )

                if metric == 'rank':
                    ax.plot(
                        df[metric].idxmin(), df[metric].min(),
                        'o', ms=15, color='orangered', alpha=0.5
                    )
                else:
                    ax.plot(
                        df[metric].idxmax(), df[metric].max(),
                        'o', ms=15, color='orangered', alpha=0.5
                    )

                if rolling_avg:
                    ts = df[metric].rolling(window_size, center=True).mean()
                    ax.plot(
                        ts,
                        color=consts.at_color,
                        lw=1,
                    )

            except ValueError as e:
                print(f'Value error for {df.index.name}: {e}.')
                pass

            ax.grid(True, which="both", axis='both', alpha=.3, lw=1, linestyle='-')
            cax.grid(True, which="both", axis='both', alpha=.3, lw=1, linestyle='-')

            cax.set_xticklabels([], minor=False)
            cax.set_xticklabels([], minor=True)

            ax.set_ylim(vmin, vmax)

            if metric == 'rank':
                ax.set_yticks(np.arange(1, 7))
                ax.invert_yaxis()
            else:
                ax.set_yticks(-1 * np.arange(2, 7))

            cax.set_ylim(0, 1)
            cax.set_yticks([0, .5, 1])
            cax.set_yticklabels(['0', '.5', '1'])
            cax.axhline(.5, color='k', lw=1)

            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_visible(False)
            ax.spines['top'].set_visible(False)

            cax.spines['right'].set_visible(False)
            cax.spines['left'].set_visible(False)

            if metric == 'rank':
                ax.text(
                    df[metric].idxmin(),
                    df[metric].min()-.6,
                    df[metric].idxmin().strftime('%Y/%m/%d'),
                    ha='center',
                    verticalalignment='center',
                    #transform=ax.transAxes,
                    color='grey'
                )
            else:
                ax.text(
                    df[metric].idxmax(),
                    df[metric].max()+.6,
                    df[metric].idxmax().strftime('%Y/%m/%d'),
                    ha='center',
                    verticalalignment='center',
                    #transform=ax.transAxes,
                    color='grey'
                )

            i += 1

            if c == 0:
                if r == 0:
                    if legend:
                        ax.legend(
                            handles=[
                                Line2D([0], [0], color=consts.rt_color, lw=2, label='RT'),
                                Line2D([0], [0], color=consts.ot_color, lw=2, label='OT'),
                            ],
                            loc='upper left',
                            bbox_to_anchor=(0, 1.1),
                            ncol=1,
                            frameon=False,
                            fontsize=11,
                        )

                cax.text(
                    -0.2, 0.5, f"RT/OT\nBalance", ha='center',
                    verticalalignment='center', transform=cax.transAxes
                )

                if metric == 'rank':
                    ax.text(
                        -0.2, 0.5, r"$\log_{10}$"+"\n"+r"$n$-gram"+"\nrank\n"+"$r$", ha='center',
                        verticalalignment='center', transform=ax.transAxes
                    )
                else:
                    ax.text(
                        -0.2, 0.5, r"$\log_{10}$"+"\nRate of\nusage\n"+"$f$", ha='center',
                        verticalalignment='center', transform=ax.transAxes
                    )

                ax.text(
                    -0.2, 0.1, "Less\nTalked\nAbout\n↓", ha='center',
                    verticalalignment='center', transform=ax.transAxes, color='grey'
                )
                ax.text(
                    -0.2, 0.9, "↑\nMore\nTalked\n About", ha='center',
                    verticalalignment='center', transform=ax.transAxes, color='grey'
                )

            if c == cols-1 and r == 0:
                cax.text(
                    .88, 1.6,
                    f"Last updated\n{df.index[-1].strftime('%Y/%m/%d')}",
                    ha='center',
                    verticalalignment='center', transform=cax.transAxes
                )

    plt.subplots_adjust(top=0.97, right=0.97, hspace=0.25)
    plt.savefig(f'{savepath}.pdf', bbox_inches='tight', pad_inches=.25)
    plt.savefig(f'{savepath}.png', dpi=300, bbox_inches='tight', pad_inches=.25)


def plot_cases(savepath, deaths, confirmed):
    """Plot a grid of contagiograms

    Args:
        savepath (pathlib.Path): path to save plot
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

    minr, maxr = 1, 10 ** 6
    major_locator = mdates.YearLocator()
    major_format = '\n%Y'
    minor_format = '%b'
    minor_locator = mdates.AutoDateLocator()
    start_date = datetime.datetime(2020, 1, 1)
    end_date = confirmed.index[-1]

    i = 0
    for r in np.arange(0, rows, step=4):
        for c in np.arange(cols):

            ax = fig.add_subplot(gs[r:r+3, c])
            tax = ax.twinx()

            ax.set_title(consts.countries[i], fontsize=14)

            ax.set_xlim(start_date, end_date)
            ax.xaxis.set_major_locator(major_locator)
            ax.xaxis.set_major_formatter(mdates.DateFormatter(major_format))
            ax.xaxis.set_minor_locator(minor_locator)
            ax.xaxis.set_minor_formatter(mdates.DateFormatter(minor_format))

            tax.set_ylim(10 ** 0, 10 ** 8)
            tax.tick_params(axis='y', labelcolor='grey')
            tax.set_xlim(start_date, end_date)
            tax.xaxis.set_major_locator(major_locator)
            tax.xaxis.set_major_formatter(mdates.DateFormatter(major_format))
            tax.xaxis.set_minor_locator(minor_locator)
            tax.xaxis.set_minor_formatter(mdates.DateFormatter(minor_format))
            tax.set_ylim(10**0, 10**8)

            ax.plot(confirmed[consts.countries[i]], color='red')
            tax.semilogy(confirmed[consts.countries[i]], color='grey')
            tax.semilogy(deaths[consts.countries[i]], color='grey', ls='--')

            ax.set_ylim(minr, maxr)
            ax.invert_yaxis()
            ax.set_yscale('log')
            ax.yaxis.set_major_locator(
                ticker.LogLocator(base=10, numticks=12)
            )
            ax.set_yticks(
                [1, 10, 10 ** 2, 10 ** 3, 10 ** 4, 10 ** 5, 10 ** 6],
                minor=False
            )
            ax.set_yticklabels(
                ['1', '10', '100', r'$10^3$', r'$10^4$', r'$10^5$', r'$10^6$'],
                minor=False,
                color='red'
            )
            ax.yaxis.set_minor_locator(
                ticker.LogLocator(base=10.0, subs=np.arange(.1, 1, step=.1), numticks=30)
            )

            if c == 0:
                ax.text(
                    -0.25, 0.5, "Average\n"+r"$n$-gram"+"\nrank\n"+r"$\langle r \rangle$", ha='center',
                    verticalalignment='center', transform=ax.transAxes, color='red'
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
                            Line2D([0], [0], color='r', lw=2, label=r'$E[\tau]$'),
                            Line2D([0], [0], color='grey', lw=2, label='Cases'),
                            Line2D([0], [0], color='grey', ls='--', lw=2, label='Deaths'),
                        ],
                        loc='upper left',
                        bbox_to_anchor=(0, 1),
                        ncol=1,
                        frameon=False,
                        fontsize=11,
                    )

            if c == 2:
                tax.set_ylabel(
                    f"Number of cases",
                    color='grey'
                )

            if c == cols - 1 and r == 0:
                ax.text(
                    .88, 1.15,
                    f"Last updated\n{confirmed.index[-1].strftime('%Y/%m/%d')}",
                    ha='center',
                    verticalalignment='center', transform=ax.transAxes
                )

            i += 1

    plt.subplots_adjust(top=0.97, right=0.97, hspace=0.25, wspace=.25)
    plt.savefig(f'{savepath}.pdf', bbox_inches='tight', pad_inches=.25)
    plt.savefig(f'{savepath}.png', dpi=300, bbox_inches='tight', pad_inches=.25)

