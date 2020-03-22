
import logging
import datetime
import pandas as pd
from query import Query
from pathlib import Path


def query_lang(
        save_path,
        lang,
        ngrams,
        usr='guest',
        pwd='roboctopus',
        case_sensitive=True,
        rt=True,
        start_date=datetime.datetime(2019, 9, 1)
):
    """Query a given language collection in the database

    Args:
        save_path (pathlib.Path): path to save generated timeseries
        lang (string): language collection
        ngrams (list): a list of ngrams to query
        usr (string): username to use to access database
        pwd (string): password to use to access database
        case_sensitive (bool): a toggle for case_sensitive lookups
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

    q = Query(usr, pwd, f'1grams', lang)

    for i, w in enumerate(ngrams):

        if Path(f'{save_path}/count.tsv').exists():
            start_date = datetime.datetime(
                datetime.date.today().year,
                datetime.date.today().month,
                datetime.date.today().day - 2
            )

        print(f"Retrieving: '{w}'")
        if case_sensitive:
            d = q.query_timeseries(w, start_time=start_date)
        else:
            d = q.query_insensitive_timeseries(w, start_time=start_date)

        for k in dfs.keys():
            if dfs.get(k) is None:
                dfs[k] = d[k].to_frame(name=w)
            else:
                dfs[k].insert(loc=dfs[k].shape[1], column=w, value=d[k].values)

    for k in dfs.keys():
        dfs[k].index.name = k
        file = Path(f'{save_path}/{k}.tsv')

        if file.exists():
            old = pd.read_csv(file, header=0, index_col=0, na_filter=False, sep='\t')
            old = old.combine_first(dfs.get(k))
            old.to_csv(file, sep='\t')
        else:
            dfs.get(k).to_csv(file, sep='\t')


def update_timeseries(save_path, languages_path, ngrams_path):
    """Query database to update timeseries

    Args:
        save_path (pathlib.Path): path to save generated timeseries
        languages_path (pathlib.Path): path to parse requested languages
        ngrams_path (pathlib.Path): path to parse requested ngrams

    """
    topk = 10
    supported_languages = pd.read_csv(languages_path, header=0, index_col=1)

    for code in supported_languages.index:
        lang = supported_languages.loc[code].Language

        for file in ngrams_path.glob(f'{code}_*.tsv'):
            print(f'\n{lang}: {file.stem}\n')

            ngrams = pd.read_csv(
                file,
                na_filter=False,
                sep='\t',
                encoding='utf8',
                quotechar=None,
                quoting=3
            ).iloc[:, 0].values[:topk]

            out = Path(f'{save_path}/{lang}/')
            out.mkdir(parents=True, exist_ok=True)

            if file.stem.endswith('no_rt'):
                query_lang(out, code, ngrams, rt=False)
            else:
                query_lang(out, code, ngrams)

        print('-' * 50)
