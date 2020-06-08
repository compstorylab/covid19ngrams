#!/usr/bin/env bash

# update n-grams timeseries
~/anaconda3/envs/storywrangler/bin/python ~/www-root/share/data/covid19ngrams/src/update.py

# update n-grams timeseries for AMT data
~/anaconda3/envs/storywrangler/bin/python ~/www-root/share/data/covid19ngrams/src/update.py mt

# udpate figures for https://arxiv.org/abs/2003.12614
~/anaconda3/envs/storywrangler/bin/python ~/www-root/share/data/covid19ngrams/src/update.py figures
