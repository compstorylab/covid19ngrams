
import sys
import time
from pathlib import Path

import cli
import utils


def parse_args(args):
    parser = cli.parser()

    parser.add_argument(
        '-l', '--langs',
        default=Path('.').resolve().parent/'data'/'languages.csv',
        help='path to language dict'
    )

    parser.add_argument(
        '-n', '--ngrams',
        default=Path('.').resolve().parent/'data'/'ngrams',
        help='absolute Path of the requested ngrams'
    )

    parser.add_argument(
        '-o', '--outdir',
        default=Path('.').resolve().parent/'data'/'timeseries',
        help='absolute Path to save timeseries'
    )

    return parser.parse_args(args)


def main(args=None):
    timeit = time.time()

    if args is None:
        args = sys.argv[1:]

    args = parse_args(args)
    Path(args.outdir).mkdir(parents=True, exist_ok=True)

    utils.update_timeseries(args.outdir, args.langs, args.ngrams)

    print(f'Total time elapsed: {time.time() - timeit:.2f} sec.')


if __name__ == "__main__":
    main()
