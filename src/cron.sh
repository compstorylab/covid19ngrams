#!/usr/bin/env bash

repo="$HOME/www-root/share/data/covid19ngrams"
script="$repo/src/update.py"
log="$repo/data/log.txt"
jhu="$HOME/www-root/share/data/COVID-19"


# update n-grams timeseries
/usr/bin/time -v -o $repo/data/resources.txt ~/anaconda3/envs/storywrangler/bin/python $script &> $log


# udpate figures for https://arxiv.org/abs/2003.12614
git -C $jhu pull
~/anaconda3/envs/storywrangler/bin/python $script figures $jhu &>> $log
