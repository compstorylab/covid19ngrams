
import sys
import time
from pathlib import Path

import utils


def main():
    timeit = time.time()
    repo = Path(sys.argv[0]).resolve().parent.parent
    langs = repo / 'data' / 'languages.csv'
    targets = repo / 'data' / 'rank_turbulence_divergence' / 'raw'
    outdir = repo / 'data' / 'rank_turbulence_divergence' / 'cleaned'

    Path(outdir).mkdir(parents=True, exist_ok=True)

    for f in targets.glob('*grams'):
        utils.filter_ngrams(
            save_path=outdir / f.stem,
            ngrams_path=targets / f.stem,
            languages_path=langs,
        )

    print(f'Total time elapsed: {time.time() - timeit:.2f} sec.')


if __name__ == "__main__":
    main()
