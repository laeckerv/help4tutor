#!/usr/bin/env python

import argparse
import logging as log
import re
from colorama import Fore
from colorama import Style
from colorama import init
from help4tutor.groupsetup import groupsetup
import help4tutor.issueuploader
import help4tutor.exercisedownloader
import help4tutor.groupsetup.groupsetup
import help4tutor.utility as util


__version__ = '0.0.2'

# TODO: Handle all exceptions
# TODO: Add update project group command
# TODO: Change checkout and upload handling: Don't get groups by config but by member file

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


def _ask_for_saving(where, func):
    if not hasattr(func, '__call__'):
        raise TypeError('parameter must be a function')

    if re.match(util.create_regex_allowed('Yy'),
                util.user_prompt('Do you want to save this at "' + where + '"?', 'Answer', 'YyNn')):
        func()
    else:
        print(Fore.RED + 'Changes were not saved.')


def _checkout(args):
    exercise_downloader = exercisedownloader.ExerciseDownloader(args.config, args.group, args.exercise,
                                                                args.dest_dir, args.clean)
    exercise_downloader.download()


def _upload(args):
    issue_uploader = issueuploader.IssueUploader(args.config, args.prefix, args.exercise, args.src_dir)
    issue_uploader.upload()


def _member(args):
    member_configurator = groupsetup.GroupSetup(args.config, args.dest_dir)
    member_configurator.get_git_groups()
    _ask_for_saving(args.dest_dir, member_configurator.save_member_file)


def _add(args):
    member_configurator = groupsetup.GroupSetup(args.config, args.src_dir)
    member_configurator.load_member_file()
    member_configurator.add_group()
    _ask_for_saving(args.src_dir, member_configurator.save_member_file)


def _show(args):
    member_configurator = groupsetup.GroupSetup(args.config, args.src_dir)
    member_configurator.load_member_file()
    if args.group:
        try:
            member_configurator.show_project_groups(args.group)
        except ValueError as v:
            print(Fore.RED + Style.BRIGHT + str(v))
    else:
        member_configurator.show_project_groups()


def _percentage(args):
    try:
        member_configurator = groupsetup.GroupSetup(args.config, args.src_dir)
        member_configurator.load_member_file()
        member_configurator.add_percentage(args.project_group, args.exercise, args.percentage)
        _ask_for_saving(args.src_dir, member_configurator.save_member_file)
    except ValueError as v:
        print(Fore.RED + Style.BRIGHT + str(v))


def _joker(args):
    try:
        member_configurator = groupsetup.GroupSetup(args.config, args.src_dir)
        member_configurator.load_member_file()
        member_configurator.add_joker(args.project_group, args.exercise, args.days)
        _ask_for_saving(args.src_dir, member_configurator.save_member_file)
    except ValueError as v:
        print(Fore.RED + Style.BRIGHT + str(v))


def _dismiss(args):
    try:
        member_configurator = groupsetup.GroupSetup(args.config, args.src_dir)
        member_configurator.load_member_file()
        if args.reset:
            member_configurator.un_dismiss(args.project_group)
        else:
            member_configurator.dismiss(args.project_group)

        _ask_for_saving(args.src_dir, member_configurator.save_member_file)
    except ValueError as v:
        print(Fore.RED + Style.BRIGHT + str(v))



def _delete(args):
    try:
        member_configurator = groupsetup.GroupSetup(args.config, args.src_dir)
        member_configurator.load_member_file()
        member_configurator.delete_project_group(args.project_group)
        _ask_for_saving(args.src_dir, member_configurator.save_member_file)
    except ValueError as v:
        print(Fore.RED + Style.BRIGHT + str(v))


def main():
    init()
    # Argument parser
    parser = argparse.ArgumentParser(description='Utility for administrating a course as tutor')
    parser.add_argument('--version', action='version', version=__version__)
    parser.add_argument('-v', '--verbosity', default=0, action='count', help='increase output verbosity')
    parser.add_argument('-c', '--config', default='.config', help='configuration file')

    # Subparser action
    subparsers = parser.add_subparsers(dest='action')
    subparsers.required = True

    # Member file configuration
    # # get all members
    parser_member_conf = subparsers.add_parser('get_members',
                                               help='Get all members of course from gitlab and save it at --src-dir (user prompt)')
    parser_member_conf.add_argument('-d', '--dest_dir', required=True,
                                    help='directory where member file should be saved')
    parser_member_conf.set_defaults(func=_member)

    ## add project group to an existing member file
    add_project_parser = subparsers.add_parser('add_project_group', help='Add new project groups (user prompt)')
    add_project_parser.add_argument('-s', '--src_dir', required=True,
                                    help='directory where member file should be changed')
    add_project_parser.set_defaults(func=_add)

    ## show groups in member file
    show_member_parser = subparsers.add_parser('show_group', help='Show specified groups')
    show_member_parser.add_argument('-s', '--src_dir', required=True,
                                    help='directory where member file should be changed')
    show_member_parser.add_argument('-g', '--group',
                                    help='if specified, only show projects groups of group. Otherwise all project groups')
    show_member_parser.set_defaults(func=_show)

    ## add percentage for a group
    percentage_parser = subparsers.add_parser('percentage',
                                              help='Adding percentages for a lab and a group (user prompt)')
    percentage_parser.add_argument('-pg', '--project_group', required=True, type=int,
                                   help='project group that should be updated')
    percentage_parser.add_argument('-e', '--exercise', required=True, help='exercise where percentage should be set')
    percentage_parser.add_argument('-p', '--percentage', required=True, help='percentage for the group')
    percentage_parser.add_argument('-s', '--src_dir', required=True,
                                   help='directory where member file should be changed')
    percentage_parser.set_defaults(func=_percentage)

    ## add joker days for a group
    joker_parser = subparsers.add_parser('joker', help='Increase joker days for a group for a lab')
    joker_parser.add_argument('-pg', '--project_group', required=True, type=int,
                              help='project group which uses joker days')
    joker_parser.add_argument('-d', '--days', required=True, help='amount of joker days')
    joker_parser.add_argument('-e', '--exercise', required=True, help='exercise where joker days are needed')
    joker_parser.add_argument('-s', '--src_dir', required=True, help='directory where member file should be changed')
    joker_parser.set_defaults(func=_joker)

    ## dismiss or un_dismiss a group
    dismiss_parser = subparsers.add_parser('dismiss', help='Dismiss a project group from lab')
    dismiss_parser.add_argument('-pg', '--project_group', required=True, type=int,
                                help='project group that should be dismissed')
    dismiss_parser.add_argument('-s', '--src_dir', required=True, help='directory where member file should be changed')
    dismiss_parser.add_argument('--reset', action="store_true", help='un-dismiss a project group')
    dismiss_parser.set_defaults(func=_dismiss)

    ## remove a project group
    delete_project_parser = subparsers.add_parser('remove_project_group', help='Remove project groups (user prompt)')
    delete_project_parser.add_argument('-pg', '--project_group', required=True, type=int,
                                       help='project group that should be removed')
    delete_project_parser.add_argument('-s', '--src_dir', required=True,
                                       help='directory where member file should be changed')
    delete_project_parser.set_defaults(func=_delete)

    ## Checkout
    parser_checkout = subparsers.add_parser('checkout',
                                            help='Checkout sources of specified groups (member file required)')
    parser_checkout.add_argument('-e', '--exercise', required=True, help='current exercise (eg. L1, L2, ...)')
    parser_checkout.add_argument('-g', '--group', required=True, help='group that should be checked out (eg. A,B,..)')
    parser_checkout.add_argument('-t', '--tag', required=True,
                                 help='tag that should be checked out (member file required)')
    parser_checkout.add_argument('-d', '--dest_dir', required=True,
                                 help='directory in which repositories should be checked out')
    parser_checkout.add_argument('--clean', action="store_true", help='WARNING: clean destination directory')
    parser_checkout.set_defaults(func=_checkout)


    # TODO: Checkout WIKI

    ## Upload results
    parser_upload = subparsers.add_parser('upload', help='Upload result files for a group.')
    parser_upload.add_argument('-p', '--prefix', required=True, help='prefix for issue title (eg. Result)')
    parser_upload.add_argument('-e', '--exercise', required=True, help='current exercise (eg. L1, L2, ...)')
    parser_upload.add_argument('-s', '--src_dir', required=True,
                               help='source directory for results (eg. /home/user/lab2014/results/')
    parser_upload.set_defaults(func=_upload)

    args = parser.parse_args()
    log.basicConfig(format='%(levelname)s: %(message)s', level=get_log_lvl(args.verbosity))
    args.func(args)



