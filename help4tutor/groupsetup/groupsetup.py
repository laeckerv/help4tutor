__author__ = 'Manuel Hieke'

import gitlab as git
import help4tutor.configloader as ldr
from getpass import *
import logging as log
import colorama
import os
import shutil
from help4tutor.groupsetup import groupdictionary
from collections import OrderedDict
from pprint import pprint
import re

class GroupSetup():
    """
    TODO:

    :author: Manuel Hieke
    """

    conf_props = ['git_url', 'git_group_name', 'git_repo_prefix', 'git_lecture_name', 'member_file']
    conf_section = 'Default'

    def __init__(self, config_file, src_dir):
        """


        :param src_dir: 
        :param config_file:
        """

        assert isinstance(config_file, str)
        self.config_file=config_file
        assert isinstance(src_dir, str)
        self.src_dir=src_dir

        loader = ldr.ConfigLoader(self.config_file)
        config = loader.loadConfig(self.conf_props, self.conf_section)

        if config == None:
            raise ImportError('Config file does not include all properties: ' + str(self.conf_props))

        self.__token = ''
        self.url = config['git_url']
        self.lecture_name = config['git_lecture_name']
        self.group_name = config['git_group_name']
        self.repo_prefix = config['git_repo_prefix']
        self.member_file = self.src_dir.rstrip('/') + '/' + config['member_file'].lstrip('/')
        self.dictAccessor = groupdictionary.GroupDictionary(5)

        colorama.init(autoreset=True)


    def save_member_file(self):
        if os.path.isfile(self.member_file):
            user_inp = self.__user_prompt('Do you want to save a copy of old member file?' 'YyNn')
            if re.match(self.__regex_allowed('Yy'), user_inp):
                shutil.copyfile( self.member_file, self.member_file + '.bkp')

        self.dictAccessor.save_in_file(self.member_file)


    def load_member_file(self):
        if os.path.isfile(self.member_file):
            self.dictAccessor.read_file(self.member_file)


    def get_git_groups(self):
        gl = git.Gitlab(self.url, self.__get_token(), verify_ssl=False)

        if gl:
            self.dictAccessor = groupdictionary.GroupDictionary(5)
            ident = [t['id'] for t in gl.getgroups(per_page=100) if t['path'] == self.group_name]
            if ident != []:
                temp_dict = {}
                for entry in gl.getgroups(ident[0])['projects']:
                    repo_name = entry['name']
                    if re.match('^' + self.lecture_name + '_[0-9]+', repo_name):
                        project_names = self.__get_project_names(gl.listprojectmembers(entry['id'])[1:3])
                        temp_dict.update({repo_name:project_names})

                final_list = OrderedDict(sorted(temp_dict.items(), key=lambda k: k[0], reverse=True))

                self.__clear_screen()
                print(u'Adding project groups into group dictionary:')
                print

                pos = 1
                while len(final_list) != 0:
                    print(u'There are {} project groups left.'.format(len(final_list)))
                    user_list = self.__user_prompt('Choose a list of project groups to add: '
                                                   , ['[1-9][0-9]*(,[1-9][0-9]*)*','done']).split(',')

                    if user_list == ['done']:
                        print(colorama.Fore.GREEN + 'List was created successfully!')
                        break

                    if not self.user_list_valid(user_list, final_list):
                        self.__clear_screen()
                        print(colorama.Fore.RED + 'Invalid list of groups:')
                        continue

                    print(u'Project groups List {}'.format(user_list))
                    print


                    user_input = self.__user_prompt('Is this list correct?', 'YyNn')

                    if re.match(self.__regex_allowed('Nn'), user_input):
                        self.__clear_screen()
                        continue

                    self.__insert_project_groups(final_list, user_list)


    def user_list_valid(self, user_list, git_list):
        ret_val = True
        for entry in user_list:
            name = self.lecture_name + '_' + entry
            if name not in git_list.keys():
                ret_val = False
                break

        return ret_val


    def __insert_project_groups(self, entries, user_list):
        existing_groups = self.dictAccessor.get_groups
        existing_groups.remove('maxJoker')
        existing_groups.append('.+')

        print(existing_groups)

        user_input = self.__user_prompt('Select group for project groups', existing_groups)

        for i in user_list:
            project_name = self.lecture_name + '_' + i
            memebers = entries.pop(key=project_name)

            self.dictAccessor.add_group(user_input)
            self.dictAccessor.add_project(user_input, project_name, memebers)

        print(u'Dictionary updated: ')
        pprint(self.dictAccessor.get_dict)


    def __user_prompt(self, question, string_check):
        user_input = ''

        if string_check != None:
            combined = self.__regex_allowed(string_check)
            user_input = raw_input(u'{0:s} [{1:s}] '.format(question, combined.replace('^','').replace('$','')))
            while re.match(combined, user_input) == None:
                user_input = raw_input(u'{0:s} [{1:s}] '.format(question, combined.replace('^','').replace('$','')))
        else:
            user_input = raw_input(question)

        return user_input


    def __regex_allowed(self, chk):
        return "(^" + "$)|(^".join(chk) + "$)"

    def __get_project_names(self, d):
        return [ entry['name'] for entry in d ]


    def __get_token(self):
        if self.__token == None:
            self.__token = getpass('Please provide private token from Gitlab (' + self.url + '):')

        return self.__token

    def __clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
