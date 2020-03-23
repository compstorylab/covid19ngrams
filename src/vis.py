
from __future__ import unicode_literals
import numpy as np
import pandas as pd

from bidi import algorithm as bidialg

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import matplotlib.dates as mdates

import warnings
warnings.simplefilter("ignore")


def plot_contagiograms(savepath, ngrams, rolling_avg=True):
    """Plot a grid of contagiograms

    Args:
        savepath (pathlib.Path): path to save plot
        ngrams (list[tuple]): a 2D-list of ngrams to plot
        rolling_avg (bool): a toggle for plotting a rolling average of the timeseries
    """

    plt.rcParams.update({
        'font.size': 10,
        'axes.titlesize': 16,
        'axes.labelsize': 14,
        'xtick.labelsize': 12,
        'ytick.labelsize': 12,
        'legend.fontsize': 12,
        'font.family': 'Arial',
    })

    vmin, vmax = -6, 0
    rows, cols = 16, 3
    fig = plt.figure(figsize=(12, 14))
    gs = fig.add_gridspec(ncols=cols, nrows=rows)
    log = "$\log_{10}$"
    at_color = 'k'
    ot_color = 'C0'
    rt_color = 'C1'
    labels = 'A B C D E F G H I J K L M N O P Q R S T U V W X Y Z'.split(' ')
    window_size = 7

    date_format = '%m\n%Y'
    major_locator = mdates.MonthLocator()
    minor_locator = mdates.AutoDateLocator()
    contagion_resolution = 'D'

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
            ax.xaxis.set_major_formatter(mdates.DateFormatter(date_format))
            ax.xaxis.set_minor_locator(minor_locator)

            cax.xaxis.set_major_locator(major_locator)
            cax.xaxis.set_major_formatter(mdates.DateFormatter(date_format))
            cax.xaxis.set_minor_locator(minor_locator)

            df.dropna(inplace=True)
            df['freq'] = df['count'] / df['count'].sum()
            df['freq_no_rt'] = df['count_no_rt'] / df['count'].sum()

            df['freq'] = df['freq'].apply(np.log10)
            df['freq_no_rt'] = df['freq_no_rt'].apply(np.log10)

            at = df['count'].resample(contagion_resolution).mean()
            ot = df['count_no_rt'].resample(contagion_resolution).mean()
            rt = at - ot

            cax.annotate(
                labels[i], xy=(-.16, 1.2), color='k', weight='bold',
                xycoords="axes fraction", fontsize=16,
            )
            cax.set_title(bidialg.get_display(df.index.name))
            #cax.set_title(df.index.name.format(fname), fontproperties=prop)

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
                    df['freq'],
                    marker='o',
                    ms=3,
                    color='grey',
                    mfc='grey',
                    mec='grey',
                    lw=0,
                )

                ax.plot(
                    df['freq'].idxmax(), df['freq'].max(),
                    'o', ms=15, color='orangered', alpha=0.5
                )

                if rolling_avg:
                    ts = df['freq'].rolling(window_size, center=True).mean()
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
            ax.set_yticks(-1 * np.arange(7))
            cax.set_ylim(0, 1)
            cax.set_yticks([0, .5, 1])
            cax.set_yticklabels(['0', '.5', '1'])
            cax.axhline(.5, color='k', lw=1)

            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_visible(False)
            ax.spines['top'].set_visible(False)

            cax.spines['right'].set_visible(False)
            cax.spines['left'].set_visible(False)

            ax.text(
                df['freq'].idxmax(),
                df['freq'].max()+.6,
                df['freq'].idxmax().strftime('%Y/%m/%d'),
                ha='center',
                verticalalignment='center',
                #transform=ax.transAxes,
                color='grey'
            )

            i += 1

            if c == 0:
                if r == 0:
                    ax.legend(
                        handles=[
                            Line2D([0], [0], color=rt_color, lw=2, label=r'$RT_{f}$'),
                            Line2D([0], [0], color=ot_color, lw=2, label=r'$OT_{f}$'),
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

    plt.subplots_adjust(top=0.97, right=0.97, hspace=0.25)
    plt.savefig(savepath + '.pdf', bbox_inches='tight', pad_inches=.25)
