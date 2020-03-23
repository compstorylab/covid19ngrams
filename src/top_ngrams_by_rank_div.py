import pandas as pd
import datetime
import glob
from collections import Counter


lang_list = [
    'en','es','pt','ar','ko','fr','id','tr','de','it','ru','tl','hi',
    'fa','ur','pl','ca','nl','ta','el','sv','sr','fi','ceb','uk'
]

begin_date = datetime.datetime(2020,3,1)
end_date = datetime.datetime(2020,3,19)
dates = pd.date_range(start=begin_date, end=end_date, freq='D')

datapth = "/users/m/v/mvarnold/covid-19-twitter-timeseries/data/"


rt_type_dict = {'count': 'count_rank_divergence.tsv',
                'count_no_rt': 'count_no_rt_rank_divergence.tsv'
                }

n = 1000

for lang in lang_list:
   for rt_type in ['count', 'count_no_rt']:

        r_div_sum = Counter()
        for file_i in glob.glob(datapth+f"{lang}_*{rt_type_dict[rt_type]}"):
            df = pd.read_csv(file_i,sep='\t', index_col='ngram')
            i = 0
            for index, row in df.iterrows():
                r_div_sum[index] += row['rank_divergence'] 
                i += 1
                if i > n:
                    break

        with open(f'../data/top_1grams/{lang}_{rt_type}.tsv','w') as f:
            for key,value in sorted(r_div_sum.items(), key=lambda k_v: k_v[1], reverse=True):
                if str(key) != 'nan':
                    f.write(str(key)+'\t'+str(value)+'\n')
