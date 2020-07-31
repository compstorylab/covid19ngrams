
import sys
import time
from pathlib import Path

import vis
import cli
import utils
import consts


def parse_args(args):
    parser = cli.parser()

    # optional subparsers
    subparsers = parser.add_subparsers(help='Arguments for specific action.', dest='dtype')
    subparsers.required = False

    ff = subparsers.add_parser(
        'figures',
        help='update figures'
    )
    ff.add_argument(
        'jhu',
        help='absolute path to the COVID-19 data repository by Johns Hopkins University'
    )

    return parser.parse_args(args)


def main(args=None):
    timeit = time.time()
    repo = Path(sys.argv[0]).resolve().parent.parent
    langs = repo/'data'/'languages.csv'
    targets = repo/'data'/'rank_turbulence_divergence'
    outdir = repo/'data'/'timeseries'
    plots = repo/'plots'

    if args is None:
        args = sys.argv[1:]

    args = parse_args(args)
    Path(outdir).mkdir(parents=True, exist_ok=True)

    if args.dtype == 'figures':

        jhu = Path(args.jhu) / 'csse_covid_19_data/csse_covid_19_time_series'
        confirmed = jhu / 'time_series_covid19_confirmed_global.csv'
        deaths = jhu / 'time_series_covid19_deaths_global.csv'
        us_confirmed = jhu / 'time_series_covid19_confirmed_US.csv'
        us_deaths = jhu / 'time_series_covid19_deaths_US.csv'

        vis.cases(
            savepath=plots / f'coronagrams_cases',
            words_by_country=consts.words_by_country,
            deaths=deaths,
            confirmed=confirmed,
            us_deaths=us_deaths,
            us_confirmed=us_confirmed,
            lang_hashtbl=Path(langs),
        )

        for k, words in consts.contagiograms.items():
            vis.contagiograms(
                savepath=plots/f'contagiograms_{k}',
                words=words,
                lang_hashtbl=Path(langs),
            )

    else:
        for f in targets.glob('*grams'):
            print(f.stem)
            utils.update_timeseries(
                save_path=outdir/f.stem,
                languages_path=langs,
                ngrams_path=targets/f.stem,
                database=f.stem.split('_')[-1]
            )

    print(f'Total time elapsed: {time.time() - timeit:.2f} sec.')


if __name__ == "__main__":
    main()
