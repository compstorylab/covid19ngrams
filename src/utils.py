
import regex as re
import datetime
import pandas as pd
import numpy as np  
from query import Query
from pathlib import Path

import logging
logger = logging.getLogger(__name__)


def filter_ngrams(save_path, ngrams_path, languages_path):
    """Filter out Twitter-specific content

    Args:
        save_path (pathlib.Path): path to save generated timeseries
        ngrams_path (pathlib.Path): path to parse requested ngrams
        languages_path (pathlib.Path): path to parse requested languages
    """
    supported_languages = pd.read_csv(languages_path, header=0, index_col=1, comment='#')
    regex = re.compile(
        r'(RT)|(rt)|'  # retweet prefix
        r'(&\S+;)|'  # html codes
        r'([^\P{P}]+)|'  # punctuations
        r'([^\P{M}]+)|'  # accents
        r'([^\P{S}]+)|'  # symbols
        r'([^\P{Z}]+)|'  # separators
        r'([^\P{C}]+)|'  # others
        r'(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+\S+)',  # links
    )

    for lang_code in supported_languages.index:
        for file in ngrams_path.glob(f'{lang_code}_*.tsv'):
            print(file)

            ngrams = pd.read_csv(
                file,
                na_filter=False,
                sep='\t',
                encoding='utf8',
                header=None,
                quotechar=None,
                quoting=3,
                names=['ngram', 'rankdiv']
            )

            out = Path(f'{save_path}')
            out.mkdir(parents=True, exist_ok=True)

            inds = []
            for k, i in enumerate(ngrams['ngram']):
                ws = i.split(' ')

                if any([bool(w.startswith('@')) for w in ws]):
                    inds.append(k)

                if any([bool(regex.findall(w)) for w in ws]):
                    inds.append(k)

            ngrams = ngrams.drop(inds)
            ngrams.set_index('ngram', inplace=True)
            ngrams.to_csv(f'{save_path / file.stem}.tsv', sep='\t', header=False)
            logger.info(f'{save_path / file.stem}.tsv')

        logger.info('-' * 50)


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
        t = datetime.date.today() - datetime.timedelta(10)
        start_date = datetime.datetime(t.year, t.month, t.day)

    q = Query(database, lang)
    logger.info(f'Starting date: {start_date.date()}')
    d_arr = q.query_timeseries_array(list(ngrams), start_time=start_date).reset_index(drop=True)

    for k in dfs.keys():
        to_update = d_arr.pivot_table(index='time', columns='word', values=k)
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
            logger.info(f'{lang}: {file.stem}\n')
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

            logger.info(f"Retrieving: {len(ngrams)} {database} ...")
            if file.stem.endswith('no_rt'):
                query_lang_array(out, lang_code, database, ngrams, rt=False)
            else:
                query_lang_array(out, lang_code, database, ngrams)

        logger.info('-' * 50)

