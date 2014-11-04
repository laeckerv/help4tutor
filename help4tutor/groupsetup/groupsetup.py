__author__ = 'Manuel Hieke'

from getpass import *

import gitlab as git

import help4tutor.configloader as ldr
import help4tutor.utility as util

# import logging as log
import colorama
import os
import shutil
from help4tutor.groupsetup import groupdictionary
from collections import OrderedDict
import re


class GroupSetup():
    """
    TODO:

    :author: Manuel Hieke
    """

    __conf_props = ['git_url', 'git_group_name', 'git_repo_prefix', 'git_lecture_name', 'member_file']
    __conf_section = 'Default'

    def __init__(self, config_file, src_dir):
        """

        :param src_dir:
        :param config_file:
        """

        assert isinstance(config_file, str)
        self.config_file = config_file
        assert isinstance(src_dir, str)
        self.src_dir = src_dir

        loader = ldr.ConfigLoader(self.config_file)
        config = loader.loadConfig(self.__conf_props, self.__conf_section)

        if not config:
            raise ImportError('Config file does not include all properties: ' + str(self.__conf_props))

        self.__token = ''
        self.__url = config['git_url']
        self.__lecture_name = config['git_lecture_name']
        self.__group_name = config['git_group_name']
        self.__repo_prefix = config['git_repo_prefix']
        self.__member_file = self.src_dir.rstrip('/') + '/' + config['member_file'].lstrip('/')
        self.__dictAccessor = groupdictionary.GroupDictionary(5)

        colorama.init(autoreset=True)


    def save_member_file(self, force=False):
        if not force and os.path.isfile(self.__member_file):
            user_inp = util.user_prompt(colorama.Style.BRIGHT + 'A file already exists (' + self.__member_file + ')\n' +
                                        colorama.Style.NORMAL + 'Do you want to save a copy of old member file?',
                                        'Answer', 'YyNn')
            if re.match(util.create_regex_allowed('Yy'), user_inp):
                shutil.copyfile(self.__member_file, self.__member_file + '.bkp')

        self.__dictAccessor.save_in_file(self.__member_file)


    def load_member_file(self):
        if os.path.isfile(self.__member_file):
            self.__dictAccessor.read_file(self.__member_file)


    def get_git_groups(self):
        self.__dictAccessor = groupdictionary.GroupDictionary(5)
        final_list = self.__get_groups_git()

        if final_list:
            self.__clear_screen()
            print(u'Adding project groups into group dictionary:')
            print

            while len(final_list) != 0:
                print(u'There are {} project groups left.'.format(len(final_list)))
                user_list = util.user_prompt('Choose a list of project groups to add: ', self.__lecture_name + '_?',
                                             ['[1-9][0-9]*(,[1-9][0-9]*)*', 'done']).split(',')

                if user_list == ['done']:
                    break

                if not self.__user_list_valid([self.__lecture_name + '_' + t for t in user_list], final_list):
                    print(colorama.Fore.RED + 'Invalid list of groups:')
                    continue

                print(u'Project groups List {}'.format(user_list))
                print

                user_input = util.user_prompt('Is this list correct?', 'Answer', 'YyNn')

                if re.match(util.create_regex_allowed('Nn'), user_input):
                    self.__clear_screen()
                    continue

                self.__insert_project_groups(final_list, user_list)

            print(colorama.Fore.GREEN + 'Dictionary was updated successfully!')


    def add_group(self):
        final_list = self.__get_groups_git()
        if final_list:
            self.__clear_screen()
            print(colorama.Style.BRIGHT + u'Groups in member file:')
            self.__dictAccessor.print_groups_overview()
            while True:
                print(colorama.Style.BRIGHT + u'Project groups which are not added yet:')
                not_added = set(final_list.keys()).difference(set(self.__dictAccessor.get_project_groups('all')))
                print(', '.join(not_added))
                print(colorama.Style.BRIGHT + u'Existing Groups:')
                groups = self.__dictAccessor.get_groups()
                print(', '.join(groups))

                user_list = util.user_prompt('Choose a list of project groups to add: ', self.__lecture_name + '_?',
                                             ['[1-9][0-9]*(,[1-9][0-9]*)*', 'done']).split(',')

                if user_list == ['done']:
                    break

                if not self.__user_list_valid([self.__lecture_name + '_' + t for t in user_list], not_added):
                    print(colorama.Fore.RED + 'Invalid list of groups')
                    continue

                print(u'Project groups List {}'.format(user_list))
                print

                user_input = util.user_prompt('Is this list correct?', 'Answer', 'YyNn')

                if re.match(util.create_regex_allowed('Nn'), user_input):
                    self.__clear_screen()
                    continue

                self.__insert_project_groups(final_list, user_list)


    def delete_project_group(self, prj):
        project = self.__lecture_name + '_' + str(prj)
        self.__dictAccessor.delete_project(project)
        print(colorama.Style.BRIGHT + 'Updated info of project group "' + project + '"')
        self.__dictAccessor.print_project(project)

    def show_project_groups(self, group=None):
        self.__dictAccessor.print_groups(group)


    def add_percentage(self, prj, lab, percentage):
        project = self.__lecture_name + '_' + str(prj)
        self.__dictAccessor.edit_result(project, lab, percentage)
        print(colorama.Style.BRIGHT + 'Updated info of project group "' + project + '"')
        self.__dictAccessor.print_project(project)


    def add_joker(self, prj, lab, days):
        project = self.__lecture_name + '_' + str(prj)
        self.__dictAccessor.edit_joker(project, lab, days)
        print(colorama.Style.BRIGHT + 'Updated info of project group "' + project + '"')
        self.__dictAccessor.print_project(project)


    def dismiss(self, prj):
        project = self.__lecture_name + '_' + str(prj)
        self.__dictAccessor.dismiss_project(project)
        print(colorama.Style.BRIGHT + 'Updated info of project group "' + project + '"')
        self.__dictAccessor.print_project(project)


    def un_dismiss(self, prj):
        project = self.__lecture_name + '_' + str(prj)
        self.__dictAccessor.un_dismiss_project(project)
        print(colorama.Style.BRIGHT + 'Updated info of project group "' + project + '"')
        self.__dictAccessor.print_project(project)


    def __get_groups_git(self):
        """
        Connects to gitlab and returns all project groups in the namespace of :__group_name

        :return:
        """
        gl = git.Gitlab(self.__url, self.__get_token(), verify_ssl=False)
        if gl:
            ident = [t['id'] for t in gl.getgroups(per_page=100) if t['path'] == self.__group_name]
            if ident != []:
                temp_dict = {}
                for entry in gl.getgroups(ident[0])['projects']:
                    repo_name = entry['name']
                    if re.match('^' + self.__lecture_name + '_[0-9]+', repo_name):
                        project_members = self.__get_project_names(gl.listprojectmembers(entry['id'])[1:3])
                        temp_dict.update({repo_name: project_members})

                return OrderedDict(sorted(temp_dict.items(), key=lambda k: k[0], reverse=True))


    def __user_list_valid(self, user_list, git_list):
        print(user_list)
        print(git_list)
        ret_val = True
        for entry in user_list:
            if entry not in git_list:
                ret_val = False
                break
        return ret_val


    def __insert_project_groups(self, entries, user_list):
        existing_groups = self.__dictAccessor.get_groups()
        existing_groups.append('.+')

        print(existing_groups)

        user_input = util.user_prompt('Select group for project groups', 'Group name', existing_groups)

        for i in user_list:
            project_name = self.__lecture_name + '_' + i
            members = entries.pop(key=project_name)

            self.__dictAccessor.add_group(user_input)
            self.__dictAccessor.add_project(user_input, project_name, members)

        print(colorama.Fore.GREEN + u'Dictionary updated.')


    def __get_project_names(self, d):
        return [entry['name'] for entry in d]


    def __get_token(self):
        if self.__token == '':
            self.__token = getpass('Please provide private token from Gitlab (' + self.__url + '):')

        return self.__token


    @staticmethod
    def __clear_screen():
        os.system('cls' if os.name == 'nt' else 'clear')
