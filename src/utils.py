
import re
import datetime
import pandas as pd
import numpy as np  
from query import Query
from pathlib import Path
import vis
import consts


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
        t = datetime.date.today() - datetime.timedelta(7)
        start_date = datetime.datetime(t.year, t.month, t.day)

    q = Query(database, lang)
    print(f'Starting date: {start_date.date()}')
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

            print(f"Retrieving: {len(ngrams)} {database} ...")
            if file.stem.endswith('no_rt'):
                query_lang_array(out, lang_code, database, ngrams, rt=False)
            else:
                query_lang_array(out, lang_code, database, ngrams)

        print('-' * 50)


def filter_ngrams(save_path, ngrams_path):
    """Filter out non-latin characters for MT

    Args:
        save_path (pathlib.Path): path to save generated timeseries
        ngrams_path (pathlib.Path): path to parse requested ngrams
    """
    save_path.mkdir(parents=True, exist_ok=True)
    filter1 = re.compile('[A-Za-z0-9]+')
    filter2 = re.compile('[0-9]+')

    for file in ngrams_path.glob(f'en_*.tsv'):
        ngrams = pd.read_csv(
            file,
            na_filter=False,
            sep='\t',
            encoding='utf8',
            header=None,
            quotechar=None,
            quoting=3
        ).iloc[:, 0].values

        ngrams_to_keep = []

        for word in ngrams:
            if '@' in word or '#' in word:
                continue
            ws = word.split()
            if not all([bool(filter1.findall(w)) for w in ws]):
                continue
            if any([bool(filter2.findall(w)) for w in ws]):
                continue

            ngrams_to_keep.append(word)

        df = pd.DataFrame(ngrams_to_keep, columns=['ngrams'])
        df.to_csv(f'{save_path/file.stem}.tsv', sep='\t')
        print(save_path)


def amt(save_path, ngrams_path):
    """Compile files for AMT

    Args:
        save_path (pathlib.Path): path to save generated timeseries
        ngrams_path (pathlib.Path): path to parse requested ngrams
    """
    save_path.mkdir(parents=True, exist_ok=True)

    for file in ngrams_path.glob('*.tsv'):
        print(file.stem)
        ngrams = pd.read_csv(
            file,
            na_filter=False,
            sep='\t',
            encoding='utf8',
            header=0,
            quotechar=None,
            quoting=3,
            index_col=0,
        ).iloc[:1000, 0].values

        print(ngrams.shape)
        partitions = np.array_split(ngrams, 10)
        for i, p in enumerate(partitions):
            print(p.shape)
            df = pd.DataFrame(p, columns=['text1'])
            df.to_csv(f'{save_path/file.stem}-{(i*100)+1:0>4d}-{(i+1)*100:0>4d}.csv', index=False)


def format_survey(save_path, survey_path):
    """Load AMT files in a dataframe

    Args:
        save_path (pathlib.Path): path to save generated dataframe
        survey_path (pathlib.Path): path to amt survey data
    """
    save_path.mkdir(parents=True, exist_ok=True)
    ts = [f'Answer.{t}.{i+1}' for i, t in enumerate(consts.topics)]

    ratings = None
    for file in survey_path.glob('*.csv'):
        df = pd.read_csv(
            file,
            header=0,
            encoding='utf8',
        )
        if ratings is None:
            ratings = df.groupby(['Input.text1'])[ts].sum()
        else:
            ratings = ratings.combine_first(
                df.groupby(['Input.text1'])[ts].sum()
            )

    ratings.columns = consts.topics
    ratings.index.name = 'ngram'
    ratings.to_csv(f'{save_path}/survey.tsv', sep='\t')


def load_data(survey_path, n1_path, n2_path, resolution='W', agg='sum', spam=False):
    """Plot a rank timeseries for each topic

    Args:
        savepath (pathlib.Path): path to save plot
        survey_path (pathlib.Path): path to survey data
        n1_path (pathlib.Path): path to 1grams timeseries
        n2_path (pathlib.Path): path to 2grams timeseries
        resolution (string): desired data resolution
        agg (string): aggregation function to use
        spam (bool): a toggle for including the spam column

    Returns: (3 x pd.DataFrame)
        Dataframes for ratings and ngram timeseries
    """

    ratings = pd.read_csv(
        survey_path,
        header=0,
        index_col=0,
        sep='\t',
    )
    if not spam:
        ratings.drop('Spam', axis=1, inplace=True)

    #ratings = ratings.div(ratings.sum(axis=1), axis=0)

    # (10) is the max number of votes for each ngram on AMT
    ratings = ratings.div(10, axis=0)

    n1 = pd.read_csv(
        n1_path,
        header=0,
        index_col=0,
        sep='\t',
    )
    n1.index = pd.to_datetime(n1.index)
    n1 = n1.loc['2020':]
    n1 = n1.resample(resolution).agg(agg)
    n1.index.name = '1grams'

    n2 = pd.read_csv(
        n2_path,
        header=0,
        index_col=0,
        sep='\t',
    )
    n2.index = pd.to_datetime(n2.index)
    n2 = n2.loc['2020':]
    n2 = n2.resample(resolution).agg(agg)
    n2.index.name = '2grams'

    return ratings, n1, n2


def compute_vol(ratings, ngrams):
    """ Compute relative volume of each topic
    Args:
        ratings (pd.DataFrame): a dataframe of topic ratings for each ngram
        ngrams: a dataframe of ngrams and their daily count, rank, freq
        n2_path (pathlib.Path): path to 2grams timeseries

    Returns: (pd.DataFrame) a dataframe relative volume of each topic
    """
    topics = ratings.loc[ngrams.columns].dropna(how='all')
    counts = ngrams[topics.index]

    df = pd.DataFrame(index=ngrams.index, columns=ratings.columns)
    for day, row in df.iterrows():
        df.loc[day] = topics.multiply(counts.loc[day].T, axis='index').sum()

    return df


def rank(savepath, survey_path, n1_path, n2_path):
    """Plot a rank timeseries for each topic

    Args:
        savepath (pathlib.Path): path to save plot
        survey_path (pathlib.Path): path to survey data
        n1_path (pathlib.Path): path to 1grams timeseries
        n2_path (pathlib.Path): path to 2grams timeseries
    """
    ratings, n1, n2 = load_data(survey_path, n1_path, n2_path, resolution='W', agg='sum')

    for n in [n1, n2]:
        ranks = compute_vol(ratings, n)
        ranks.index = ranks.index.strftime('%d\n%b')
        last = ranks.index[-1]
        ranks = ranks.T.reset_index()

        for col in ranks.loc[:, ranks.columns != 'index']:
            ranks[col] = ranks[col].rank(ascending=False)
            ranks[col] = ranks[col].loc[ranks[col] <= 8]

        ranks = ranks.dropna(thresh=2).fillna(9)
        ranks = ranks.sort_values(last)

        vis.plot_rank(
            f'{savepath}/topic_ranks_{n.index.name}',
            ranks
        )


def stack(savepath, survey_path, n1_path, n2_path):
    """
    Plot a stackplot timeseries for each topic

    Args:
        savepath (pathlib.Path): path to save plot
        survey_path (pathlib.Path): path to survey data
        n1_path (pathlib.Path): path to 1grams timeseries
        n2_path (pathlib.Path): path to 2grams timeseries
    """
    ratings, n1, n2 = load_data(survey_path, n1_path, n2_path, resolution='D', agg='sum')

    for n in [n1, n2]:
        counts = compute_vol(ratings, n)
        vis.stackplot(
            f'{savepath}/topic_stackplot_{n.index.name}',
            counts
        )


def violin(savepath, survey_path, n1_path, n2_path):
    """
    Plot a violinplot timeseries for each topic

    Args:
        savepath (pathlib.Path): path to save plot
        survey_path (pathlib.Path): path to survey data
        n1_path (pathlib.Path): path to 1grams timeseries
        n2_path (pathlib.Path): path to 2grams timeseries
    """
    ratings, n1, n2 = load_data(survey_path, n1_path, n2_path, resolution='D', agg='sum')

    for n in [n1, n2]:
        counts = compute_vol(ratings, n)
        vis.violinplot(
            f'{savepath}/topic_violinplot_{n.index.name}',
            counts
        )
