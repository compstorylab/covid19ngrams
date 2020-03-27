import datetime
import numpy as np
import pandas as pd
from pymongo import MongoClient
from pymongo.collation import Collation, CollationStrength


class Query:
    """Class to work with n-gram db"""

    def __init__(self, db, lang, username='guest', pwd='roboctopus'):
        """Python wrapper to access database on hydra.uvm.edu

        Args:
            db: database to use
            lang: language collection to use
            username: username to access database
            pwd: password to access database
        """
        client = MongoClient(f'mongodb://{username}:{pwd}@hydra.uvm.edu:27017')
        db = client[db]
        self.tweets = db[lang]
        self.lang = lang

    def query_timeseries(self, word=None, start_time=None):
        """Query database for n-gram timeseries, return pandas dataframe

        Args:
            word (string): target ngram
            start_time (datetime): starting date for the query

        Returns (pd.DataFrame):
            dataframe of count, rank, and frequency over time for an n-gram
        """
        cols = ['count', 'count_no_rt', 'rank', 'rank_no_rt', 'freq', 'freq_no_rt']
        db_cols = ['counts', 'count_noRT', 'rank', 'rank_noRT', 'freq', 'freq_noRT']

        if start_time:
            query = {'word': word, 'time': {'$gte': start_time}}
            start = start_time
        else:
            query = {'word': word}
            start = datetime.datetime(2019, 9, 1)

        data = {
            d: {c: np.nan for c in cols}
            for d in pd.date_range(
                start=start.date(),
                end=datetime.datetime.today().date(),
                freq='D'
            ).date
        }

        for i in self.tweets.find(query):
            d = i['time'].date()
            for c, db in zip(cols, db_cols):
                data[d][c] = i[db]

        df = pd.DataFrame.from_dict(data=data, orient='index')
        df.index = pd.to_datetime(df.index)
        df.index.name = word
        return df

    def query_timeseries_array(self, word_list=None, start_time=None):
        """

        Args:
            word_list (list): list of strings to query mongo
            start_time (datetime): starting date for query

        Returns (pd.DataFrame):
            d_df dataframe of count, rank, and frequency over time for list of n-grams

        """
        db_cols = {
            'counts': 'count',
            'count_noRT': 'count_no_rt',
            'rank': 'rank',
            'rank_noRT': 'rank_no_rt',
            'freq': 'freq',
            'freq_noRT': 'freq_no_rt',
            'word': 'word',
        }

        if start_time:
            query = {'word': {'$in': word_list}, 'time': {'$gte': start_time}}
            start = start_time
        else:
            query = {'word': {'$in': word_list}}
            start = datetime.datetime(2019, 9, 1)

        df = pd.DataFrame(list(self.tweets.find(query)))
        df.set_index('word', inplace=True, drop=False)

        tl_df = pd.DataFrame(word_list)
        tl_df.set_index(0, inplace=True)

        df = tl_df.join(df)
        df['word']=df.index
        df.drop('_id', axis=1, inplace=True)
        df.rename(columns=db_cols, inplace=True)
        return df

    def query_insensitive_timeseries(self, word=None, start_time=None):
        """Query database for n-gram timeseries (case-insensitiv), return pandas dataframe

        Args:
            word (string): target ngram
            start_time (datetime): starting date for the query

        Returns (pd.DataFrame):
            dataframe of count, rank, and frequency over time for an n-gram
        """
        cols = ['count', 'count_no_rt', 'rank', 'rank_no_rt', 'freq', 'freq_no_rt']
        db_cols = ['counts', 'count_noRT', 'rank', 'rank_noRT', 'freq', 'freq_noRT']

        if start_time:
            query = {'word': word, 'time': {'$gte': start_time}}
            start = start_time
        else:
            query = {'word': word}
            start = datetime.datetime(2019, 9, 1)

        data = {
            d: {c: np.nan for c in cols}
            for d in pd.date_range(
                start=start.date(),
                end=datetime.datetime.today().date(),
                freq='D'
            ).date
        }

        for i in self.tweets.find(query).collation(
                Collation(locale=self.lang, strength=CollationStrength.SECONDARY)
        ):
            d = i['time'].date()
            for c, db in zip(cols, db_cols):
                if np.isnan(data[d][c]):
                    data[d][c] = i[db]
                else:
                    data[d][c] += i[db]

        df = pd.DataFrame.from_dict(data=data, orient='index')
        df.index = pd.to_datetime(df.index)
        df.index.name = word
        return df
