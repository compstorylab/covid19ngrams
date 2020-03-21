import datetime
import subprocess
import pandas as pd
from dateutil.relativedelta import relativedelta
import time
from multiprocessing import Pool

def run_lang(lang):
    for rt_type in ['count','count_no_rt']:
        for date2 in dates:
            date1 = date2 + relativedelta(weeks=-52)
            command = f"python rank_divergence.py --date1 {date1.strftime('%Y-%m-%d')} --date2 {date2.strftime('%Y-%m-%d')} --lang {lang} --rt_type {rt_type}"
            print(command)
            subprocess.call(command, shell=True)

begin_date = datetime.datetime(2020,3,1)
end_date = datetime.datetime(2020,3,19)

dates = pd.date_range(start=begin_date, end=end_date, freq='D')

lang_list = ['en','es','pt','ar','ko','fr','id','tr','de','it','ru','tl','hi','fa','ur','pl','ca','nl','ta','el','sw ','sr','fi','ceb','uk']

with Pool(10) as p:
    p.map(run_lang, lang_list)
