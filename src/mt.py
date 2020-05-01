
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

    parser.add_argument(
        '-t', '--targets',
        default=Path('.').resolve().parent/'data'/'rank_turbulence_divergence',
        help='absolute Path of the requested targets'
    )

    parser.add_argument(
        '-o', '--outdir',
        default=Path('.').resolve().parent/'data'/'mt',
        help='absolute Path to save filtered ngrams'
    )

    return parser.parse_args(args)


def main(args=None):
    timeit = time.time()

    if args is None:
        args = sys.argv[1:]

    args = parse_args(args)
    Path(args.outdir).mkdir(parents=True, exist_ok=True)

    if args.dtype == 'filter':
        for f in args.targets.glob('*grams'):
            print(f.stem)
            utils.filter_ngrams(
                save_path=args.outdir / f.stem,
                ngrams_path=args.targets / f.stem
            )
    elif args.dtype == 'compile':
        utils.amt(
            save_path=args.outdir/'amt',
            ngrams_path=args.outdir/'targets'
        )

    elif args.dtype == 'format':
        utils.format_survey(
            save_path=args.outdir,
            survey_path=args.outdir/'survey'
        )
    else:
        print('Error: unknown action!')

    print(f'Total time elapsed: {time.time() - timeit:.2f} sec.')


if __name__ == "__main__":
    main()
