
import sys
import time
from pathlib import Path
import matplotlib.pyplot as plt

import cli
import vis
import utils


def parse_args(args):
    parser = cli.parser()

    # optional subparsers
    subparsers = parser.add_subparsers(help='Arguments for specific action.', dest='dtype')
    subparsers.required = True

    subparsers.add_parser(
        'contagiograms',
        help='Plot a grid of contagiograms: rate of usage timeseries + contagion fractions'
    )

    subparsers.add_parser(
        'adj',
        help='Plot a adjacency matrix of topics'
    )

    subparsers.add_parser(
        'network',
        help='Plot a network of topics'
    )

    subparsers.add_parser(
        'rank',
        help='Plot a rank timeseries of topics'
    )

    subparsers.add_parser(
        'stack',
        help='Plot a stackplot timeseries of topics'
    )

    subparsers.add_parser(
        'violin',
        help='Plot a violinplot timeseries of topics'
    )

    subparsers.add_parser(
        'heatmaps',
        help='Plot heatmaps of top ngrams by topics'
    )

    return parser.parse_args(args)


def main(args=None):
    plt.rcParams.update({
        'font.size': 10,
        'axes.titlesize': 16,
        'axes.labelsize': 14,
        'xtick.labelsize': 12,
        'ytick.labelsize': 12,
        'legend.fontsize': 12,
        'font.family': 'serif',
    })

    timeit = time.time()
    repo = Path(sys.argv[0]).resolve().parent.parent
    langs = repo/'data'/'languages.csv'
    mt = repo/'data'/'mt'
    survey = mt/'survey.tsv'
    ts_1grams = mt/'timeseries'/'april_1grams'
    ts_2grams = mt/'timeseries'/'april_2grams'
    outdir = repo/'plots'

    if args is None:
        args = sys.argv[1:]

    args = parse_args(args)
    Path(args.outdir).mkdir(parents=True, exist_ok=True)

    if args.dtype == 'contagiograms':
        vis.contagiograms(
            savepath=Path(outdir),
            lang_hashtbl=Path(langs),
        )
    elif args.dtype == 'adj':
        vis.adj(
            savepath=Path(outdir),
            survey_path=Path(survey)
        )
    elif args.dtype == 'network':
        vis.network(
            savepath=Path(outdir),
            survey_path=Path(survey)
        )
    elif args.dtype == 'rank':
        utils.rank(
            savepath=Path(outdir),
            survey_path=Path(survey),
            n1_path=Path(ts_1grams)/'count.tsv',
            n2_path=Path(ts_2grams)/'count.tsv',
        )
    elif args.dtype == 'stack':
        utils.stack(
            savepath=Path(outdir),
            survey_path=Path(survey),
            n1_path=Path(ts_1grams)/'count.tsv',
            n2_path=Path(ts_2grams)/'count.tsv',
        )
    elif args.dtype == 'heatmaps':
        vis.heatmaps(
            savepath=Path(outdir),
            survey_path=Path(survey)
        )
    elif args.dtype == 'violin':
        utils.violin(
            savepath=Path(outdir),
            survey_path=Path(survey),
            n1_path=Path(ts_1grams)/'count.tsv',
            n2_path=Path(ts_2grams)/'count.tsv',
        )
    else:
        print('Error: unknown action!')

    print(f'Total time elapsed: {time.time() - timeit:.2f} sec.')


if __name__ == "__main__":
    main()
