import os
import sys
import datetime
import subprocess
import pandas as pd
import argparse
import numpy as np
from dateutil.relativedelta import relativedelta   


def date_exists(date, pth="../../data/tmp/", lang='en'):
    """ ensure 1gram rank file in the right place """
    datestr = date.strftime(format='%Y-%m-%d')
    thayer_pth = '/users/t/a/talshaab/scratch/storywrangler/storyons/1grams/'
    if not os.path.isdir(pth+lang):
        os.mkdir(pth+lang)

    if not os.path.isfile(pth+lang+'/'+lang+'_'+datestr+'.tsv'):
        if os.path.isfile(thayer_pth+datestr+'.tar.gz'):
            subprocess.call(['bash','/users/m/v/mvarnold/matlab/allotaxonometer/figures/storywrangler/unpack_tar.sh', datestr, lang])
        else:
            print('File does not exist',date)
            raise OSError

def figure_exists(date,date2, pth="figallotaxonometer9000"):
    """quit if figure already exists """
    fig_name = f'figallotaxonometer9000-{date.strftime(format="%Y-%m-%d")}-{date2.strftime(format="%Y-%m-%d")}-rank-div-alpha-third_noname.pdf'
    if os.path.isfile(pth+fig_name):
        raise OSError    


def make_rank_divergence(date1, date2, lang='en', rt_type='count'):
    """ make a rank divergence plots between two days on twitter

    :param date1: old date
    :param date2: new date
    :param lang: language tag to use
    :param rt_type: organic or all ['count', 'count_no_rt']
    """

    print(os.getcwd()) 
    # make sure files exist
    date1 = datetime.datetime.strptime(date1,'%Y-%m-%d')
    date2 = datetime.datetime.strptime(date2,'%Y-%m-%d')
    try:
        figure_exists(date1,date2)
        date_exists(date1, lang=lang)
        date_exists(date2, lang=lang)

        # call matlab script
        datestr1 = date1.strftime(format='%Y %m %d')
        datestr2 = date2.strftime(format='%Y %m %d')
        subprocess.call(['/gpfs1/arch/x86_64-rhel7/matlab2017b/bin/matlab',
            '-nodesktop',
            '-nosplash',
            '-r',
            f"cd('/users/m/v/mvarnold/matlab/allotaxonometer/figures/storywrangler'); figtwitter([{datestr1}],[{datestr2}],'{lang}', '{rt_type}'); exit"],
            cwd='/users/m/v/mvarnold/matlab/allotaxonometer/figures/storywrangler')
    except OSError:
        pass

def rank_divergence(r1, r2, alpha=1/3):
    return ((alpha+1) / alpha) * (np.abs( (1 / r1) ** (alpha) - (1 / r2) ** (alpha)) **(1/(1+alpha))) 


def compute_rank_divergence(date1, date2, lang='en', rt_type='count', alpha=1/3):

    pth = '~/matlab/allotaxonometer/data/tmp/'

    date1i = datetime.datetime.strptime(date1,'%Y-%m-%d')
    date2i = datetime.datetime.strptime(date2,'%Y-%m-%d')
    try:   
        date_exists(date1i, lang=lang)
        date_exists(date2i, lang=lang)
    except OSError:
        pass
    
    df1 = pd.read_csv(f"{pth}{lang}/{lang}_{date1}.tsv", sep='\t')
    df2 = pd.read_csv(f"{pth}{lang}/{lang}_{date2}.tsv", sep='\t')
    
    df_merged = df1[['ngram',rt_type]].merge(df2[['ngram', rt_type]],on='ngram',suffixes=('_1','_2'))
    for i in ['1','2']:
        df_merged[f'rank_{i}'] = df_merged[f'{rt_type}_{i}'].rank(ascending=False)
    
    df_merged['rank_divergence'] = df_merged.apply(lambda x: rank_divergence(x['rank_1'], x['rank_2'], alpha), axis=1)
    return df_merged[['ngram','rank_divergence']]


def parse_args():

    parser = argparse.ArgumentParser(description="run rank divergence plots")
    parser.add_argument('--date1', type=str)
    parser.add_argument('--date2', type=str)
    parser.add_argument('--lang', type=str, default='en')
    parser.add_argument('--rt_type', type=str, default='count')
    parser.add_argument('-p', '--plot', action='store_true')
    args = parser.parse_args()
    return args

def main():
    
    args = parse_args()

    if args.plot:
        make_rank_divergence(args.date1, args.date2, args.lang, args.rt_type)
    
    else:
        df = compute_rank_divergence(args.date1, args.date2, args.lang, args.rt_type)
        print(df.to_string())
        
if __name__ == "__main__":
    main()
