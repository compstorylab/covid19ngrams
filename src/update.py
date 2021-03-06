
import sys
import time
import logging
from pathlib import Path
from datetime import datetime
import contagiograms

import vis
import cli
import utils
import consts


logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def main(args=None):
    timeit = time.time()
    repo = Path(sys.argv[0]).resolve().parent.parent
    langs = repo/'data'/'languages.csv'
    targets = repo/'data'/'rank_turbulence_divergence'
    outdir = repo/'data'/'timeseries'
    plots = repo/'plots'

    args = cli.parse_args(args)
    Path(outdir).mkdir(parents=True, exist_ok=True)

    if args.dtype == 'figures':

        jhu = Path(args.jhu) / 'csse_covid_19_data/csse_covid_19_time_series'
        confirmed = jhu / 'time_series_covid19_confirmed_global.csv'
        deaths = jhu / 'time_series_covid19_deaths_global.csv'
        us_confirmed = jhu / 'time_series_covid19_confirmed_US.csv'
        us_deaths = jhu / 'time_series_covid19_deaths_US.csv'

        contagiograms.plot(
            consts.contagiograms,
            savepath=plots,
            start_date=datetime(2020, 1, 1),
            t1="1W",
            t2=7,
        )
        
        vis.cases(
            savepath=plots / f'coronagrams_cases',
            words_by_country=consts.words_by_country,
            deaths=deaths,
            confirmed=confirmed,
            us_deaths=us_deaths,
            us_confirmed=us_confirmed,
            lang_hashtbl=Path(langs),
        )

    else:
        for f in targets.rglob('*grams'):
            logging.info(f'{f.parent.stem}|{f.stem}')

            utils.update_timeseries(
                save_path=outdir/f.parent.stem/f.stem,
                languages_path=langs,
                ngrams_path=f,
                database=f.stem.split('_')[-1]
            )

    logging.info(f'Total time elapsed: {time.time() - timeit:.2f} sec.')


if __name__ == "__main__":
    main()
