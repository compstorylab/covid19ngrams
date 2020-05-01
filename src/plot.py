
import sys
import time
from pathlib import Path

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

    parser.add_argument(
        '-s', '--survey',
        default=Path('.').resolve().parent/'data'/'mt'/'survey.tsv',
        help='path to AMT survey data'
    )

    parser.add_argument(
        '--ts_1grams',
        default=Path('.').resolve().parent/'data'/'timeseries'/'april_top_1grams',
        help='path to 1grams timeseries'
    )

    parser.add_argument(
        '--ts_2grams',
        default=Path('.').resolve().parent/'data'/'timeseries'/'april_top_2grams',
        help='path to 2grams timeseries'
    )

    parser.add_argument(
        '-l', '--langs',
        default=Path('.').resolve().parent/'data'/'languages.csv',
        help='path to language dict'
    )

    parser.add_argument(
        '-o', '--outdir',
        default=Path('.').resolve().parent/'plots',
        help='absolute Path to save figures'
    )

    return parser.parse_args(args)


def main(args=None):
    timeit = time.time()

    if args is None:
        args = sys.argv[1:]

    args = parse_args(args)
    Path(args.outdir).mkdir(parents=True, exist_ok=True)

    if args.dtype == 'contagiograms':
        vis.contagiograms(
            savepath=Path(args.outdir),
            lang_hashtbl=Path(args.langs),
        )
    elif args.dtype == 'adj':
        vis.adj(
            savepath=Path(args.outdir),
            survey_path=Path(args.survey)
        )
    elif args.dtype == 'network':
        vis.network(
            savepath=Path(args.outdir),
            survey_path=Path(args.survey)
        )
    elif args.dtype == 'rank':
        utils.rank(
            savepath=Path(args.outdir),
            survey_path=Path(args.survey),
            n1_path=Path(args.ts_1grams)/'English'/'count.tsv',
            n2_path=Path(args.ts_2grams)/'English'/'count.tsv',
        )
    elif args.dtype == 'stack':
        utils.stack(
            savepath=Path(args.outdir),
            survey_path=Path(args.survey),
            n1_path=Path(args.ts_1grams)/'English'/'count.tsv',
            n2_path=Path(args.ts_2grams)/'English'/'count.tsv',
        )
    elif args.dtype == 'heatmaps':
        vis.heatmaps(
            savepath=Path(args.outdir),
            survey_path=Path(args.survey)
        )
    elif args.dtype == 'violin':
        utils.violin(
            savepath=Path(args.outdir),
            survey_path=Path(args.survey),
            n1_path=Path(args.ts_1grams)/'English'/'count.tsv',
            n2_path=Path(args.ts_2grams)/'English'/'count.tsv',
        )
    else:
        print('Error: unknown action!')

    print(f'Total time elapsed: {time.time() - timeit:.2f} sec.')


if __name__ == "__main__":
    main()
