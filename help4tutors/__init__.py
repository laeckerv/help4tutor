#!/usr/bin/env python

import argparse
import logging as log
import configparser
from issueuploader import IssueUploader
from exercisedownloader import ExerciseDownloader

__version__ = '0.0.1'

def get_loglvl(verbosity, minimum=3):
    VERBOSITY_LOGLEVEL = {0: log.CRITICAL,
                          1: log.ERROR,
                          2: log.WARNING,
                          3: log.INFO,
                          4: log.DEBUG}
    verbosity += minimum
    if verbosity > list(VERBOSITY_LOGLEVEL.keys())[-1]:
        return list(VERBOSITY_LOGLEVEL.keys())[-1]
    else:
        return VERBOSITY_LOGLEVEL[verbosity]

def parseConfig(args):
    config = configparser.ConfigParser()

    # TODO Check if file exists
    config.read(args.config)

    args.url = config['DEFAULT']['GitlabUrl']


def checkout(args):
    exercise_downloader = ExerciseDownloader(args.url, args.groups, args.exercise, args.dest_dir)
    exercise_downloader.download()

def upload(args):
    issue_uploader = IssueUploader(args.url, args.prefix, args.exercise, args.src_dir)
    issue_uploader.upload()

def main():

    parser = argparse.ArgumentParser(description='Utility for administrating a course as tutor')
    parser.add_argument('--version', action='version', version=__version__)
    parser.add_argument('-v', '--verbosity', default=0, action='count', help='increase output verbosity')
    parser.add_argument('-c', '--config', default='.config', help='configuration file')
    parser.add_argument('exercise', help='current exercise (eg. L1, L2, ...)')

    # Subparser action
    subparsers = parser.add_subparsers(dest='action')
    subparsers.required = True

    ## Checkout
    parser_checkout = subparsers.add_parser('checkout')
    parser_checkout.add_argument('group', help='group that should be checked out')
    parser_checkout.add_argument('tag', help='tag that should be checked out')
    parser_checkout.add_argument('dest_dir', help='directory in which repositories should be checked out')
    parser_checkout.set_defaults(func=checkout)

    ## Upload results
    parser_upload = subparsers.add_parser('upload')
    parser_upload.add_argument('prefix', help='prefix for issue title (eg. Result)')
    parser_upload.add_argument('src_dir', help='source directory for results (eg. /home/user/lab2014/results/')
    parser_upload.set_defaults(func=upload)

    args = parser.parse_args()
    log.basicConfig(format='%(levelname)s: %(message)s', level=get_loglvl(args.verbosity))
    parseConfig(args)
    args.func(args)


main()



