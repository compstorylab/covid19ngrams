import datetime
import pandas as pd
from query import Query
from pathlib import Path


def query_lang(
        save_path,
        lang,
        ngrams,
        case_sensitive=True,
        rt=True,
        start_date=datetime.datetime(2019, 9, 1)
):
    """Query a given language collection in the database

    Args:
        save_path (pathlib.Path): path to save generated timeseries
        lang (string): language collection
        ngrams (list): a list of ngrams to query
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

    q = Query(f'1grams', lang)

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


def query_lang_array(
        save_path,
        lang,
        ngrams,
        rt=True,
        start_date=datetime.datetime(2019, 9, 1)
):
    """Query a given language collection in the database

    Args:
        save_path (pathlib.Path): path to save generated timeseries
        lang (string): language collection
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
            datetime.date.today().day - 2
        )

    q = Query(f'1grams', lang)
    d_arr = q.query_timeseries_array(list(ngrams), start_time=start_date)
    print(d_arr.dropna().shape)
    print(d_arr.tail(20))
    #print(d_arr.columns)

    print((set(ngrams).difference(d_arr.word.dropna())))

    for k in dfs.keys():
        to_update = d_arr.pivot(index='time', columns='word', values=k)
        to_update = to_update[to_update.index == to_update.index] # remvoe NaTs in index
        dfs[k] = to_update
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
    topk = 1000
    supported_languages = pd.read_csv(languages_path, header=0, index_col=1, comment='#')

    for code in supported_languages.index:
        lang = supported_languages.loc[code].Language

        for file in ngrams_path.glob(f'{code}_*.tsv'):
            print(f'\n{lang}: {file.stem}\n')

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

            if file.stem.endswith('no_rt'):
                query_lang_array(out, code, ngrams, rt=False)
            else:
                query_lang_array(out, code, ngrams)

        print('-' * 50)


def contagiograms(
        savepath,
        lang_hashtbl,
        usr='guest',
        pwd='roboctopus',
        case_sensitive=True,
        start_date = datetime.datetime(2019, 12, 1)
):
    """ Plot a grid of contagiograms

    Args:
        savepath (pathlib.Path): path to save generated plot
        lang_hashtbl (pathlib.Path): path to parse requested languages
        usr (string): username to use to access database
        pwd (string): password to use to access database
        case_sensitive (bool): a toggle for case_sensitive lookups
    """
    n = 12
    ngrams = []
    supported_languages = pd.read_csv(lang_hashtbl, header=0, index_col=1, comment='#')

    virus = [
        ('virus', 'en'), ('virus', 'es'), ('vírus', 'pt'), ('فيروس', 'ar'),
        ('바이러스', 'ko'), ('virus', 'fr'), ('virus', 'id'), ('virüs', 'tr'),
        ('Virus', 'de'), ('virus', 'it'), ('вирус', 'ru'), ('virus', 'tl'),
        ('virus', 'hi'), ('ویروس', 'fa'), ('وائرس', 'ur'), ('wirus', 'pl'),
        ('virus', 'ca'), ('virus', 'nl'), ('virus', 'ta'), ('ιός', 'el'),
        ('virus', 'sv'), ('вирус', 'sr'), ('virus', 'fi'), ('вірус', 'uk'),
    ]

    contagiograms = [
        ('coronavirus', 'en'), ('cuarentena', 'es'), ('corona', 'pt'), ('كورونا', 'ar'),
        ('코로나', 'ko'), ('quarantaine', 'fr'), ('virus', 'id'), ('virüs', 'tr'),
        ('Quarantäne', 'de'), ('quarantena', 'it'), ('карантин', 'ru'), ('virus', 'tl'),
        ('virus', 'hi'), ('قرنطینه', 'fa'), ('مرضی', 'ur'), ('testów', 'pl'),
        ('confinament', 'ca'), ('virus', 'nl'), ('ரஜ', 'ta'), ('σύνορα', 'el'),
        ('Italien', 'sv'), ('mere', 'sr'), ('manaa', 'fi'), ('BARK', 'uk'),
    ]

    for i, (w, lang) in enumerate(contagiograms[:n]):
        n = len(w.split())
        print(f"Retrieving {supported_languages.loc[lang].Language}: {n}gram -- '{w}'")

        q = Query(usr, pwd, f'{n}grams', lang)

        if case_sensitive:
            d = q.query_timeseries(w, start_time=start_date)
        else:
            d = q.query_insensitive_timeseries(w, start_time=start_date)

        print(f"Highest rank: {d['rank'].min()} -- {d['rank'].idxmin().date()}")
        d.index.name = f"{supported_languages.loc[lang].Language}\n'{w}'"
        d.index.name = f"{supported_languages.loc[lang].Language}\n'{w}'"
        ngrams.append(d)

    vis.plot_contagiograms(
        f'{savepath}/contagiograms',
        ngrams,
        metric='rank'
    )
    print(f'Saved: {savepath}/contagiograms')

