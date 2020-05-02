
from __future__ import unicode_literals
import numpy as np
import pandas as pd
import seaborn as sns
import networkx as nx
import datetime
from query import Query

from bidi import algorithm as bidialg

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.lines import Line2D
import matplotlib.colors as mcolors
import matplotlib.colorbar as colorbar
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

import utils

import warnings
warnings.simplefilter("ignore")


def contagiograms(
        savepath,
        lang_hashtbl,
        case_sensitive=True,
        start_date=datetime.datetime(2019, 12, 1)
):
    """ Plot a grid of contagiograms

    Args:
        savepath (pathlib.Path): path to save generated plot
        lang_hashtbl (pathlib.Path): path to parse requested languages
        case_sensitive (bool): a toggle for case_sensitive lookups
        start_date (datetime): starting date for the query
    """
    n = 12
    ngrams = []
    supported_languages = pd.read_csv(lang_hashtbl, header=0, index_col=1, comment='#')

    virus = [
        ('virus', 'en'), ('virus', 'es'), ('vírus', 'pt'), ('فيروس', 'ar'),
        ('바이러스', 'ko'), ('virus', 'fr'), ('virus', 'id'), ('virüs', 'tr'),
        ('Virus', 'de'), ('virus', 'it'), ('вирус', 'ru'), ('virus', 'tl'),
        ('virus', 'hi'), ('ویروس', 'fa'), ('وائرس', 'ur'), ('wirus', 'pl'),
        ('virus', 'ca'), ('virus', 'nl'), ('virus', 'ta'), ('ιός', 'el'),
        ('virus', 'sv'), ('вирус', 'sr'), ('virus', 'fi'), ('вірус', 'uk'),
    ]

    contagiograms = [
        ('coronavirus', 'en'), ('cuarentena', 'es'), ('corona', 'pt'), ('كورونا', 'ar'),
        ('코로나', 'ko'), ('quarantaine', 'fr'), ('virus', 'id'), ('virüs', 'tr'),
        ('Quarantäne', 'de'), ('quarantena', 'it'), ('карантин', 'ru'), ('virus', 'tl'),
        ('virus', 'hi'), ('قرنطینه', 'fa'), ('مرضی', 'ur'), ('testów', 'pl'),
        ('confinament', 'ca'), ('virus', 'nl'), ('ரஜ', 'ta'), ('σύνορα', 'el'),
        ('Italien', 'sv'), ('mere', 'sr'), ('manaa', 'fi'), ('BARK', 'uk'),
    ]

    contagiograms2 = [
        ('social distancing', 'en'), ('coronavirus cases', 'en'), ('tested positive', 'en'), ('a pandemic', 'en'),
        ('wash your', 'en'), ('from home', 'en'), ('confirmed cases', 'en'), ('hand sanitizer', 'en'),
        ('laid off', 'en'), ('panic buying', 'en'), ('stay home', 'en'), ('toilet paper', 'en'),
    ]

    for i, (w, lang) in enumerate(contagiograms[:n]):
        n = len(w.split())
        print(f"Retrieving {supported_languages.loc[lang].Language}: {n}gram -- '{w}'")

        q = Query(f'{n}grams', lang)

        if case_sensitive:
            d = q.query_timeseries(w, start_time=start_date)
        else:
            d = q.query_insensitive_timeseries(w, start_time=start_date)

        print(f"Highest rank: {d['rank'].min()} -- {d['rank'].idxmin().date()}")
        d.index.name = f"{supported_languages.loc[lang].Language}\n'{w}'"
        d.index.name = f"{supported_languages.loc[lang].Language}\n'{w}'"
        ngrams.append(d)

    plot_contagiograms(
        f'{savepath}/contagiograms',
        ngrams,
        metric='rank'
    )
    print(f'Saved: {savepath}/contagiograms')


def plot_contagiograms(savepath, ngrams, rolling_avg=True, metric='freq'):
    """Plot a grid of contagiograms

    Args:
        savepath (pathlib.Path): path to save plot
        ngrams (list[tuple]): a 2D-list of ngrams to plot
        rolling_avg (bool): a toggle for plotting a rolling average of the timeseries
        metric (string): plot either rate of usage (freq) or rank of work (rank)
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

    date_format = '%m\n%Y'
    major_locator = mdates.MonthLocator()
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
            ax.xaxis.set_major_formatter(mdates.DateFormatter(date_format))
            ax.xaxis.set_minor_locator(minor_locator)

            cax.xaxis.set_major_locator(major_locator)
            cax.xaxis.set_major_formatter(mdates.DateFormatter(date_format))
            cax.xaxis.set_minor_locator(minor_locator)

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
            cax.set_title(bidialg.get_display(df.index.name))

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


def adj(savepath, survey_path):
    """Plot a adjacency matrix of AMT topics

    Args:
        savepath (pathlib.Path): path to save plot
        survey_path (pathlib.Path): path to survey data
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

    bins = True
    normalized = True

    ratings = pd.read_csv(survey_path, header=0, index_col=0, sep='\t')
    adj_1grams = pd.crosstab(ratings.columns, ratings.columns)
    adj_1grams.index.name = '1grams'
    adj_2grams = pd.crosstab(ratings.columns, ratings.columns)
    adj_2grams.index.name = '2grams'

    for ngram, row in ratings.iterrows():
        links = row[row != 0].to_dict()

        if len(ngram.split(' ')) > 1:
            for ll in links:
                adj_2grams.loc[ll, links] += 1
        else:
            for ll in links:
                adj_1grams.loc[ll, links] += 1

    for net in [adj_1grams, adj_2grams]:
        if normalized:
            net /= np.sum(np.diagonal(net.values))

        print(net)

        vmin = .04
        step = .01 if normalized else 100
        vmax = np.max(net.values)

        bounds = np.arange(vmin, vmax+step, step)
        cmap = plt.cm.get_cmap('magma_r')
        cmaplist = [cmap(i) for i in range(cmap.N)]
        cmaplist[0] = (1, 1, 1, 1.0)  # force the first color entry to be white
        cmap = mcolors.LinearSegmentedColormap.from_list(None, cmaplist, cmap.N)
        norm = mcolors.BoundaryNorm(bounds, cmap.N)
        mask = np.triu(np.ones_like(net, dtype=np.bool), k=1)
        annot = np.zeros_like(net.values)
        np.fill_diagonal(annot, np.diagonal(net.values))
        annot = annot.astype('str')
        annot[annot == '0'] = ''

        fig, ax = plt.subplots(figsize=(7, 5))

        if bins:
            cbarax = inset_axes(
                ax,
                width="100%",
                height="5%",
                bbox_to_anchor=(0, .1, 1, 1),
                bbox_transform=ax.transAxes,
                borderpad=.25,
            )

            ax = sns.heatmap(
                ax=ax,
                data=net,
                #mask=mask,
                cbar_ax=cbarax,
                cbar=True,
                cmap=cmap,
                norm=norm,
                vmin=vmin,
                vmax=vmax,
                annot=False if normalized else annot,
                fmt=''
            )

            ax.tick_params(
                axis='x',
                which='both',
                bottom=False,
                labelbottom=True
            )

            cb = colorbar.ColorbarBase(
                cbarax,
                cmap=cmap,
                norm=norm,
                spacing='uniform',
                ticks=bounds,
                boundaries=bounds,
                orientation='horizontal',
                extend='both'
            )

            cbarax.tick_params(labelsize=14)
            cbarax.xaxis.set_ticks_position('top')
            cbarax.yaxis.set_label_position('left')
            if normalized:
                cbarax.set_title(f'Fraction of votes ({net.index.name})')
            else:
                cbarax.set_title(f'Number of votes ({net.index.name})')

        else:
            ax = sns.heatmap(
                ax=ax,
                data=net,
                #mask=mask,
                cbar=True,
                cmap='magma_r',
                vmin=vmin,
                vmax=vmax,
                annot=annot,
                fmt=''
            )
        ax.set_xlabel('')
        ax.set_ylabel('')
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45)

        plt.tight_layout()

        if normalized:
            plt.savefig(
                f'{savepath}/normalized_topics_adjacency_matrix_{net.index.name}.pdf', bbox_inches='tight', pad_inches=.25
            )
        else:
            plt.savefig(
                f'{savepath}/topics_adjacency_matrix_{net.index.name}.pdf', bbox_inches='tight',
                pad_inches=.25
            )


def network(savepath, survey_path):
    """Plot a network of AMT topics

    Args:
        savepath (pathlib.Path): path to save plot
        survey_path (pathlib.Path): path to survey data
    """
    ratings = pd.read_csv(survey_path, header=0, index_col=0, sep='\t')
    net_1grams = pd.crosstab(ratings.columns, ratings.columns)
    net_2grams = pd.crosstab(ratings.columns, ratings.columns)

    for ngram, row in ratings.iterrows():
        links = row[row != 0].to_dict()

        if len(ngram.split(' ')) > 1:
            for ll in links:
                net_2grams.loc[ll, links] += 1
        else:
            for ll in links:
                net_1grams.loc[ll, links] += 1

    target = net_1grams
    idx = target.columns.union(target.index)
    net = target.reindex(index=idx, columns=idx, fill_value=0)
    net /= np.sum(np.max(net, axis=0))
    print(net)

    G = nx.from_numpy_matrix(net.values)
    mapping = dict(zip(G, net.columns))
    G = nx.relabel_nodes(G, mapping)
    cmap = plt.cm.magma

    nwgts = np.array([float(val) for node, val in nx.pagerank_numpy(G).items()])
    nwgts *= 10**4 / np.max(nwgts)

    # scale edge-weights [0-10]
    ewgts = np.array(list(G.edges.data('weight', default=0)))[:, 2].astype(float)
    ewgts *= 15 / np.max(ewgts)

    fig, ax = plt.subplots(figsize=(16, 12))
    pos = nx.circular_layout(G)

    nodes = nx.draw_networkx_nodes(G, pos=pos, node_list=G.nodes(), node_color='C0',
                                   node_shape='.', node_size=nwgts,)
    edges = nx.draw_networkx_edges(G, pos=pos, edgelist=G.edges(), arrows=False, width=ewgts,
                                   edge_color=ewgts, edge_cmap=cmap, alpha=.6)

    nx.draw_networkx_labels(G, pos, font_family='sans-serif', ax=ax, font_size=20, font_color='w')

    ax.axis('off')
    plt.style.use('dark_background')
    plt.tight_layout()
    plt.savefig(
        f'{savepath}/topics_network.pdf', bbox_inches='tight', pad_inches=.25
    )


def heatmaps(savepath, survey_path):
    """Plot a rank timeseries for each topic

    Args:
        savepath (pathlib.Path): path to save plot
        survey_path (pathlib.Path): path to survey data
    """
    plt.rcParams.update({
        'font.size': 10,
        'axes.titlesize': 16,
        'axes.labelsize': 14,
        'xtick.labelsize': 12,
        'ytick.labelsize': 12,
        'legend.fontsize': 12,
    })
    vmin = 0
    vmax = 1
    n = 25

    ratings = pd.read_csv(
        survey_path,
        header=0,
        index_col=0,
        sep='\t',
    )
    ratings = ratings.div(ratings.sum(axis=1), axis=0)

    n1 = ratings[ratings.index.str.split(' ').str.len() == 1]
    n1.index.name = '1grams'

    n2 = ratings[ratings.index.str.split(' ').str.len() > 1]
    n2.index.name = '2grams'

    for ngrams in [n1, n2]:
        fig, axes = plt.subplots(figsize=(16, 16), nrows=2, ncols=4)
        axes = axes.flatten()

        bounds = np.arange(0, 1.1, .1)
        cmap = plt.cm.get_cmap('magma_r')
        cmaplist = [cmap(i) for i in range(cmap.N)]
        cmaplist[0] = (1, 1, 1, 1.0)  # force the first color entry to be white
        cmap = mcolors.LinearSegmentedColormap.from_list(None, cmaplist, cmap.N)
        norm = mcolors.BoundaryNorm(bounds, cmap.N)

        for topic, ax in zip(ngrams.columns, axes):
            ax.set_title(topic)
            mat = ngrams.sort_values(topic, ascending=False).iloc[:n]

            cbarax = inset_axes(
                axes[2],
                width="500%",
                height="2%",
                bbox_to_anchor=(.75, .1, 1, 1),
                bbox_transform=axes[2].transAxes,
                borderpad=.25,
            )

            ax = sns.heatmap(
                mat,
                ax=ax,
                cbar_ax=cbarax,
                cbar=True,
                cmap=cmap,
                norm=norm,
                vmin=vmin,
                vmax=vmax,
                linewidths=0.1,
                linecolor='k',
            )

            ax.tick_params(
                axis='x',
                which='both',
                bottom=False,
                labelbottom=True
            )
            ax.set_ylabel('')
            ax.grid(False, which="both")

            cb = colorbar.ColorbarBase(
                cbarax,
                cmap=cmap,
                norm=norm,
                spacing='uniform',
                ticks=bounds,
                boundaries=bounds,
                orientation='horizontal',
                extend='both'
            )

            cbarax.tick_params(labelsize=14)
            cbarax.xaxis.set_ticks_position('top')
            cbarax.yaxis.set_label_position('left')
            cbarax.set_title('Fraction of votes')

            plt.tight_layout()

        plt.savefig(f'{savepath}/heatmaps_{ngrams.index.name}.pdf', bbox_inches='tight', pad_inches=.25)


def plot_rank(savepath, ranks):
    """Plot a rank plot of AMT topics

    Args:
        savepath (pathlib.Path): path to save plot
        ranks (pd.DataFrame): pandas dataframe of topics and their ranks
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

    rows, cols = 6, 6
    n = ranks.shape[0]

    fig = plt.figure(figsize=(10, 6))
    gs = fig.add_gridspec(ncols=cols, nrows=rows)

    ax = fig.add_subplot(gs[:, :])
    colors = {
        'Pandemic': 'C0',
        'Health': 'C1',
        'Economics': 'C2',
        'Politics': 'C3',
        'Religion': 'C4',
        'Education': 'C5',
        'Entertainment': 'C6'
    }
    colors = [colors[t] for t in ranks['index']]

    ax = pd.plotting.parallel_coordinates(
        ranks, ax=ax, class_column='index',
        color=colors, lw=5, axvlines=False,
        alpha=.75
    )
    #ax.tick_params(axis='x', rotation=45)

    ax.legend_.remove()
    lines, labels = ax.get_legend_handles_labels()
    for line, label in zip(lines, labels):
        y = line.get_ydata()

        if y[0] <= n:
            ax.annotate(
                label, xy=(0, y[0]), xytext=(-6, 0), color=line.get_color(),
                xycoords=ax.get_yaxis_transform(), textcoords="offset points",
                size=16, va="center", ha='right'
            )

        if y[-1] <= n:
            ax.annotate(
                label, xy=(1, y[-1]), xytext=(6, 0), color=line.get_color(),
                xycoords=ax.get_yaxis_transform(), textcoords="offset points",
                size=16, va="center"
            )

    ax.set_ylim(.5, n + .5)
    ax.set_yticks(range(1, n + 1))
    ax.set_yticklabels([], ha='left')
    ax.invert_yaxis()

    ax2 = ax.twinx()
    ax2.set_ylim(.5, n + .5)
    ax2.set_yticks(range(1, n + 1))
    ax2.set_yticklabels([], ha='right')
    ax2.invert_yaxis()

    ax.spines["top"].set_alpha(0.0)
    ax.spines["bottom"].set_alpha(1.0)
    ax.spines["right"].set_alpha(0.0)
    ax.spines["left"].set_alpha(0.0)
    ax.grid(True, which="both", alpha=.4, lw=1, linestyle='--')

    plt.savefig(f'{savepath}.pdf', bbox_inches='tight', pad_inches=.25)


def stackplot(savepath, counts):
    """Plot a rank plot of AMT topics

    Args:
        savepath (pathlib.Path): path to save plot
        ranks (pd.DataFrame): pandas dataframe of topics and their ranks
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

    fig, nax = plt.subplots(figsize=(10, 6))

    counts = counts.divide(counts.sum(axis=1), axis=0)
    nax = counts.plot.area(stacked=True, ax=nax, alpha=.75)

    nax.set_ylabel(f'Relative rate of usage')
    nax.set_xlabel("")
    nax.set_ylim(0, 1)
    nax.set_xlim(counts.index[0], counts.index[-1])
    nax.grid(True, which="both", axis='both', zorder=0, alpha=.3, linestyle='-')

    nax.xaxis.set_major_locator(mdates.MonthLocator())
    nax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
    nax.xaxis.set_minor_locator(mdates.DayLocator())
    plt.setp(nax.xaxis.get_majorticklabels(), ha='center', rotation=45)

    nax.legend_.remove()
    ss = 0
    lines, labels = nax.get_legend_handles_labels()
    for i, label in enumerate(labels):
        d = counts.index[0]
        ss += counts.loc[d, label]
        nax.annotate(
            label,
            xy=(d, ss - .065),
            xytext=(6, 0), color='k',
            xycoords='data',
            textcoords="offset points",
            size=14, va="center"
        )

    plt.tight_layout()
    plt.savefig(f'{savepath}.pdf', bbox_inches='tight', pad_inches=.25)


def violinplot(savepath, counts):
    """Plot a violin plot of AMT topics

    Args:
        savepath (pathlib.Path): path to save plot
        ranks (pd.DataFrame): pandas dataframe of topics and their ranks
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

    fig, ax = plt.subplots(figsize=(10, 6))
    topics = counts.columns
    counts = pd.melt(counts.reset_index(), value_vars=topics, var_name='topic', value_name='vol')

    ax = sns.swarmplot(
        ax=ax,
        data=counts,
        x="topic",
        y="vol",
        orient='v',
        marker='h',
        alpha=.75,
        edgecolors='face',
    )

    ax.set_ylim(counts.vol.min()-10**5, counts.vol.max()+10**5)
    ax.set_xlabel('')
    ax.set_ylabel('Volume')
    ax.grid(True, which="both", axis='both', zorder=0, alpha=.3, linestyle='-')
    ax.ticklabel_format(axis='y', style='sci', useMathText=True, scilimits=(0, 3))

    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)

    plt.savefig(f'{savepath}.pdf', bbox_inches='tight', pad_inches=.25)

