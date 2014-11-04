__author__ = 'mahieke'

import re

def user_prompt(question, info, check):
    '''

    :param question:
    :param info:
    :param check:
    :return:
    '''

    if check:
        combined = create_regex_allowed(check)
        user_input = raw_input(u'{0:s} [{1:s}]\n{2:s}:'.format(question, combined.replace('^', '').replace('$', ''), info))
        while not re.match(combined, user_input):
            user_input = raw_input(u'{0:s} [{1:s}]\n{2:s}: '.format(question, combined.replace('^', '').replace('$', ''), info))
    else:
        user_input = raw_input(u'{0:s}\n{1:s}:'.format(question, info))

    return user_input

def create_regex_allowed(chk):
    if isinstance(chk, basestring) or isinstance(chk, list):
        return "(^" + "$)|(^".join(chk) + "$)"