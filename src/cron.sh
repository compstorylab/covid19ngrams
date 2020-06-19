#!/usr/bin/env bash

# update n-grams timeseries
~/anaconda3/envs/storywrangler/bin/python -u ~/www-root/share/data/covid19ngrams/src/update.py &> ~/www-root/share/data/covid19ngrams/data/log.txt

# update n-grams timeseries for AMT data
~/anaconda3/envs/storywrangler/bin/python -u ~/www-root/share/data/covid19ngrams/src/update.py mt &>> ~/www-root/share/data/covid19ngrams/data/log.txt

# udpate figures for https://arxiv.org/abs/2003.12614
~/anaconda3/envs/storywrangler/bin/python -u ~/www-root/share/data/covid19ngrams/src/update.py figures &>> ~/www-root/share/data/covid19ngrams/data/log.txt