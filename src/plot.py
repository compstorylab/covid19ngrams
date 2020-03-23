
import sys
import time
from pathlib import Path

import cli
import utils


def parse_args(args):
    parser = cli.parser()

    # optional subparsers
    subparsers = parser.add_subparsers(help='Arguments for specific action.', dest='dtype')
    subparsers.required = True

    contagiograms_parser = subparsers.add_parser(
        'contagiograms',
        help='Plot a grid of contagiograms: rate of usage timeseries + contagion fractions'
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
        utils.contagiograms(
            savepath=Path(args.outdir),
            lang_hashtbl=Path(args.langs)
        )
    else:
        print('Error: unknown action!')

    print(f'Total time elapsed: {time.time() - timeit:.2f} sec.')


if __name__ == "__main__":
    main()
