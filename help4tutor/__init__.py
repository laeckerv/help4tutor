#!/usr/bin/env python

import argparse
import logging as log
import help4tutor.issueuploader
import help4tutor.exercisedownloader
from colorama import init

__version__ = '0.0.2'

def get_log_lvl(verbosity, minimum=3):
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

def checkout(args):
    exercise_downloader = exercisedownloader.ExerciseDownloader(args.config, args.group, args.exercise,
                                                                args.dest_dir, args.clean)
    exercise_downloader.download()

def upload(args):
    issue_uploader = issueuploader.IssueUploader(args.config, args.prefix, args.exercise, args.src_dir)
    issue_uploader.upload()

def main():
    # Init colorama
    init()

    # Argument parser
    parser = argparse.ArgumentParser(description='Utility for administrating a course as tutor')
    parser.add_argument('--version', action='version', version=__version__)
    parser.add_argument('-v', '--verbosity', default=0, action='count', help='increase output verbosity')
    parser.add_argument('-c', '--config', default='.config', help='configuration file')
    parser.add_argument('-e', '--exercise', required=True, help='current exercise (eg. L1, L2, ...)')

    # Subparser action
    subparsers = parser.add_subparsers(dest='action')
    subparsers.required = True

    ## Checkout
    parser_checkout = subparsers.add_parser('checkout')
    parser_checkout.add_argument('-g', '--group', required=True, help='group that should be checked out (eg. 1,2,..)')
    parser_checkout.add_argument('-t', '--tag', required=True, help='tag that should be checked out')
    parser_checkout.add_argument('-d', '--dest_dir', required=True, help='directory in which repositories should be checked out')
    parser_checkout.add_argument('--clean', help='WARNING: clean destination directory')
    parser_checkout.set_defaults(func=checkout)

    # TODO: Checkout WIKI

    ## Upload results
    parser_upload = subparsers.add_parser('upload')
    parser_upload.add_argument('-p', '--prefix', required=True, help='prefix for issue title (eg. Result)')
    parser_upload.add_argument('-s', '--src_dir', required=True, help='source directory for results (eg. /home/user/lab2014/results/')
    parser_upload.set_defaults(func=upload)

    args = parser.parse_args()
    log.basicConfig(format='%(levelname)s: %(message)s', level=get_log_lvl(args.verbosity))
    args.func(args)