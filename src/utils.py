
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
        start_date=datetime.datetime(2020, 1, 1)
):
    """Query a given language collection in the database

    Args:
        save_path (string): path to save generated timeseries
        lang (string): language collection
        ngrams (list): a list of ngrams to query
        usr (string): username to use to access database
        pwd (string): password to use to access database
        case_sensitive (bool): a toggle for case_sensitive lookups
        start_date (datetime): starting date for the query
    """
    for i, w in enumerate(ngrams):
        n = len(w.split())
        q = Query(usr, pwd, f'{n}grams', lang)
        file = Path(f'{save_path}/{w}.csv')

        if file.exists():
            start_date = datetime.datetime(
                datetime.date.today().year,
                datetime.date.today().month,
                datetime.date.today().day - 2
            )

        print(f"Retrieving {lang}: {n}gram -- '{w}'")
        if case_sensitive:
            d = q.query_timeseries(w, start_time=start_date)
        else:
            d = q.query_insensitive_timeseries(w, start_time=start_date)

        if file.exists():
            df = pd.read_csv(file, header=0, index_col=0)
            df = df.combine_first(d)
            df.to_csv(file)
        else:
            d.to_csv(file)


def update_timeseries(save_path, languages_path, ngrams_path):
    """Query database to update timeseries

    Args:
        save_path (string): path to save generated timeseries
        languages_path (string): path to parse requested languages
        ngrams_path (string): path to parse requested ngrams

    """
    supported_languages = pd.read_csv(languages_path, header=0, index_col=1)

    for code in supported_languages.index:
        lang = supported_languages.loc[code].Language
        ngrams = pd.read_csv(f'{ngrams_path}/{lang}.csv', header=0, na_filter=False).ngram.values

        out = Path(f'{save_path}/{lang}')
        out.mkdir(parents=True, exist_ok=True)
        query_lang(out, code, ngrams)
        print('-' * 50)
