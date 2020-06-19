
import sys
import time
from pathlib import Path

import vis
import cli
import utils


def parse_args(args):
    parser = cli.parser()

    # optional subparsers
    subparsers = parser.add_subparsers(help='Arguments for specific action.', dest='dtype')
    subparsers.required = False

    subparsers.add_parser(
        'mt',
        help='update timeseries for AMT survey'
    )

    subparsers.add_parser(
        'figures',
        help='update figures'
    )

    return parser.parse_args(args)


def main(args=None):
    timeit = time.time()
    repo = Path(sys.argv[0]).resolve().parent.parent
    langs = repo/'data'/'languages.csv'
    targets = repo/'data'/'rank_turbulence_divergence'
    outdir = repo/'data'/'timeseries'
    mt = repo/'data'/'mt'

    if args is None:
        args = sys.argv[1:]

    args = parse_args(args)
    Path(outdir).mkdir(parents=True, exist_ok=True)

    if args.dtype == 'mt':
        p = mt/'ngrams'
        for f in p.glob('*grams.tsv'):
            print(f.stem)
            utils.update_mtts(
                save_path=mt/'timeseries'/f.stem,
                ngrams_path=f,
                database=f.stem.split('_')[-1]
            )
    elif args.dtype == 'figures':
        contagiograms = {
            'virus_12': [
                ('virus', 'en'), ('virus', 'es'), ('vírus', 'pt'), ('فيروس', 'ar'),
                ('바이러스', 'ko'), ('virus', 'fr'), ('virus', 'id'), ('virüs', 'tr'),
                ('Virus', 'de'), ('virus', 'it'), ('вирус', 'ru'), ('virus', 'tl'),
            ],
            'virus_24': [
                ('virus', 'hi'), ('ویروس', 'fa'), ('وائرس', 'ur'), ('wirus', 'pl'),
                ('virus', 'ca'), ('virus', 'nl'), ('virus', 'ta'), ('ιός', 'el'),
                ('virus', 'sv'), ('вирус', 'sr'), ('virus', 'fi'), ('вірус', 'uk'),
            ],
            'samples_1grams_12': [
                ('coronavirus', 'en'), ('cuarentena', 'es'), ('corona', 'pt'), ('كورونا', 'ar'),
                ('바이러스', 'ko'), ('quarantaine', 'fr'), ('virus', 'id'), ('virüs', 'tr'),
                ('Quarantäne', 'de'), ('quarantena', 'it'), ('карантин', 'ru'), ('virus', 'tl'),
            ],
            'samples_1grams_24': [
                ('virus', 'hi'), ('قرنطینه', 'fa'), ('مرضی', 'ur'), ('testów', 'pl'),
                ('confinament', 'ca'), ('virus', 'nl'), ('ரஜ', 'ta'), ('σύνορα', 'el'),
                ('Italien', 'sv'), ('mere', 'sr'), ('manaa', 'fi'), ('BARK', 'uk'),
            ],
            'samples_2grams': [
                ('social distancing', 'en'), ('coronavirus cases', 'en'), ('tested positive', 'en'), ('a pandemic', 'en'),
                ('wash your', 'en'), ('from home', 'en'), ('confirmed cases', 'en'), ('hand sanitizer', 'en'),
                ('laid off', 'en'), ('panic buying', 'en'), ('stay home', 'en'), ('toilet paper', 'en'),
            ],
        }

        for k, words in contagiograms.items():
            vis.contagiograms(
                savepath=Path('.').resolve().parent/'plots'/f'contagiograms_{k}',
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
