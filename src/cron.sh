#!/usr/bin/env bash

repo="$HOME/www-root/share/data/covid19ngrams"
script="$repo/src/update.py"
log="$repo/data/log.txt"
profiler="/usr/bin/time -v -o $repo/data/resources.txt"
env="$HOME/anaconda3/envs/storywrangler/bin/python"
jhu="$HOME/www-root/share/data/COVID-19"


# update n-grams timeseries
"$profiler $env -u $script &> $log"


# udpate figures for https://arxiv.org/abs/2003.12614
git -C "$jhu" pull
"$profiler $env -u $script figures $jhu &>> $log"
