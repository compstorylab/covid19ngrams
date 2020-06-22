
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

    subparsers.add_parser(
        'filter',
        help='Filter non-latin characters for MT'
    )

    subparsers.add_parser(
        'compile',
        help='Compile files for AMT'
    )

    subparsers.add_parser(
        'format',
        help='Clean AMT files'
    )

    return parser.parse_args(args)


def main(args=None):
    timeit = time.time()
    repo = Path(sys.argv[0]).resolve().parent.parent
    ngrams = repo/'data'/'rank_turbulence_divergence'
    outdir = repo/'data'/'mt'

    if args is None:
        args = sys.argv[1:]

    args = parse_args(args)
    Path(outdir).mkdir(parents=True, exist_ok=True)

    if args.dtype == 'filter':
        for f in ngrams.glob('*grams'):
            print(f.stem)
            utils.filter_ngrams(
                save_path=outdir / f.stem,
                ngrams_path=ngrams / f.stem
            )
    elif args.dtype == 'compile':
        utils.amt(
            save_path=outdir/'amt',
            ngrams_path=outdir/'ngrams'
        )

    elif args.dtype == 'format':
        utils.format_survey(
            save_path=outdir,
            survey_path=outdir/'survey'
        )
    else:
        print('Error: unknown action!')

    print(f'Total time elapsed: {time.time() - timeit:.2f} sec.')


if __name__ == "__main__":
    main()
