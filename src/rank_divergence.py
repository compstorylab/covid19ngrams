import os
import sys
import datetime
import subprocess
import pandas as pd
import argparse
from dateutil.relativedelta import relativedelta


def date_exists(date, pth="../../data/tmp/", lang='en'):
    """ ensure 1gram rank file in the right place """
    datestr = date.strftime(format='%Y-%m-%d')
    thayer_pth = '/users/t/a/talshaab/scratch/storywrangler/storyons/1grams/'

    if not os.path.isfile(pth+datestr+'.tsv'):
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


def make_rank_divergence(date1, date2):
    """ make a rank divergence plots between two days on twitter

    :param date1: old date
    :param date2: new date
    """

    print(os.getcwd())
    # make sure files exist
    date1 = datetime.datetime.strptime(date1,'%Y-%m-%d')
    date2 = datetime.datetime.strptime(date2,'%Y-%m-%d')
    try:
        figure_exists(date1,date2)
        date_exists(date1)
        date_exists(date2)

        # call matlab script
        datestr1 = date1.strftime(format='%Y %m %d')
        datestr2 = date2.strftime(format='%Y %m %d')
        subprocess.call(['/gpfs1/arch/x86_64-rhel7/matlab2017b/bin/matlab',
            '-nodesktop',
            '-nosplash',
            '-r',
            f"cd('/users/m/v/mvarnold/matlab/allotaxonometer/figures/storywrangler'); figtwitter([{datestr1}],[{datestr2}]); exit"],
            cwd='/users/m/v/mvarnold/matlab/allotaxonometer/figures/storywrangler')
    except OSError:
        pass

def parse_args():

    parser = argparse.ArgumentParser(description="run rank divergence plots")
    parser.add_argument('--date1', type=str)
    parser.add_argument('--date2', type=str)
    args = parser.parse_args()
    return args

def main():

    args = parse_args()

    make_rank_divergence(args.date1, args.date2)


if __name__ == "__main__":
    main()
