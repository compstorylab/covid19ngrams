import datetime
import pandas as pd
import numpy as np  
from query import Query
from pathlib import Path


def query_lang_array(
        save_path,
        lang,
        database,
        ngrams,
        rt=True,
        start_date=datetime.datetime(2019, 9, 1)
):
    """Query a given language collection in the database

    Args:
        save_path (pathlib.Path): path to save generated timeseries
        lang (string): language collection
        database (string): database codename
        ngrams (list): a list of ngrams to query
        rt (bool): a toggle to include retweets
        start_date (datetime): starting date for the query
    """
    if rt:
        dfs = {
            'count': None,
            'rank': None,
            'freq': None
        }
    else:
        dfs = {
            'count_no_rt': None,
            'rank_no_rt': None,
            'freq_no_rt': None
        }

    if Path(f'{save_path}/count.tsv').exists():
        start_date = datetime.datetime(
            datetime.date.today().year,
            datetime.date.today().month,
            datetime.date.today().day - 6
        )

    q = Query(database, lang)
    d_arr = q.query_timeseries_array(list(ngrams), start_time=start_date)

    for k in dfs.keys():
        to_update = d_arr.pivot(index='time', columns='word', values=k)
        to_update = to_update[to_update.index == to_update.index]  # remove NaTs in index
        dfs[k] = to_update
        dfs[k].index.name = k
        file = Path(f'{save_path}/{k}.tsv')

        if file.exists():
            old = pd.read_csv(file, header=0, index_col=0, na_filter=False, sep='\t')
            old[old == ''] = np.nan

            old = old.combine_first(dfs.get(k))
            old.to_csv(file, sep='\t')
        else:
            dfs.get(k).to_csv(file, sep='\t')


def update_timeseries(save_path, languages_path, ngrams_path, database):
    """Query database to update timeseries

    Args:
        save_path (pathlib.Path): path to save generated timeseries
        languages_path (pathlib.Path): path to parse requested languages
        ngrams_path (pathlib.Path): path to parse requested ngrams
        database (string): database codename
    """
    topk = 1000
    supported_languages = pd.read_csv(languages_path, header=0, index_col=1, comment='#')

    for lang_code in supported_languages.index:
        lang = supported_languages.loc[lang_code].Language

        for file in ngrams_path.glob(f'{lang_code}_*.tsv'):
            print(f'{lang}: {file.stem}\n')
            ngrams = pd.read_csv(
                file,
                na_filter=False,
                sep='\t',
                encoding='utf8',
                header=None,
                quotechar=None,
                quoting=3
            ).iloc[:, 0].values[:topk]

            out = Path(f'{save_path}/{lang}/')
            out.mkdir(parents=True, exist_ok=True)

            print(f"Retrieving: '{len(ngrams)} {database} ...'")
            if file.stem.endswith('no_rt'):
                query_lang_array(out, lang_code, database, ngrams, rt=False)
            else:
                query_lang_array(out, lang_code, database, ngrams)

        print('-' * 50)
