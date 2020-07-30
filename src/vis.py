
from __future__ import unicode_literals
import numpy as np
import pandas as pd
import datetime
from query import Query

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.lines import Line2D
from bidi import algorithm as bidialg

import consts

import warnings
warnings.simplefilter("ignore")


def contagiograms(
        savepath,
        words,
        lang_hashtbl,
        case_sensitive=True,
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

        if case_sensitive:
            d = q.query_timeseries(w, start_time=start_date)
        else:
            d = q.query_insensitive_timeseries(w, start_time=start_date)

        print(f"Top rank: {d['rank'].min()} -- {d['rank'].idxmin().date()}")
        d.index.name = f"{supported_languages.loc[lang].Language}\n'{w}'"
        d.index.name = f"{supported_languages.loc[lang].Language}\n'{w}'"
        ngrams.append(d)

    plot_contagiograms(savepath, ngrams, metric='rank')
    print(f'Saved: {savepath}')


def plot_contagiograms(savepath, ngrams, rolling_avg=True, metric='rank'):
    """Plot a grid of contagiograms

    Args:
        savepath (pathlib.Path): path to save plot
        ngrams (list[tuple]): a 2D-list of ngrams to plot
        rolling_avg (bool): a toggle for plotting a rolling average of the timeseries
        metric (string): plot either rate of usage (freq) or rank of work (rank)
    """

    rows, cols = 16, 3
    fig = plt.figure(figsize=(12, 14))
    gs = fig.add_gridspec(ncols=cols, nrows=rows)
    log = "$\log_{10}$"
    at_color = 'k'
    ot_color = 'C0'
    rt_color = 'C1'
    labels = 'A B C D E F G H I J K L M N O P Q R S T U V W X Y Z'.split(' ')
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
                labels[i], xy=(-.16, 1.2), color='k', weight='bold',
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
                    color=ot_color
                )
                cax.plot(
                    rt / at,
                    lw=1,
                    color=rt_color
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
                        color=at_color,
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
                                Line2D([0], [0], color=rt_color, lw=2, label='RT'),
                                Line2D([0], [0], color=ot_color, lw=2, label='OT'),
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
                        -0.2, 0.5, f"{log}\nWord\nRank", ha='center',
                        verticalalignment='center', transform=ax.transAxes
                    )
                else:
                    ax.text(
                        -0.2, 0.5, f"{log}\nRate of\nUsage", ha='center',
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
