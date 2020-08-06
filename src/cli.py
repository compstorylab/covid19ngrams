
import argparse
from argparse import ArgumentDefaultsHelpFormatter
from operator import attrgetter


class SortedMenu(ArgumentDefaultsHelpFormatter):
    def add_arguments(self, actions):
        actions = sorted(actions, key=attrgetter('option_strings'))
        super(SortedMenu, self).add_arguments(actions)


def parse_args(args):
    """ Util function to parse command-line arguments """
    parser = argparse.ArgumentParser(
        formatter_class=SortedMenu,
        description='COVID-19 ngram timeseries \
        Copyright (c) 2020 The Computational Story Lab. Licensed under the MIT License;'
    )

    # optional subparsers
    subparsers = parser.add_subparsers(help='Arguments for specific action.', dest='dtype')
    subparsers.required = False

    ff = subparsers.add_parser(
        'figures',
        help='update figures'
    )
    ff.add_argument(
        'jhu',
        help='absolute path to the COVID-19 data repository by Johns Hopkins University'
    )

    return parser.parse_args(args)
