import subprocess
import shutil
import os
from colorama import Fore, Back, Style
import help4tutor.configloader as ldr
from help4tutor.utility import get_input as input


class ExerciseDownloader():
    """
    TODO:

    :author: Lars Eckervogt
    """

    conf_props = ['git_url', 'group_1', 'group_2', 'group_3', 'group_4', 'groups', 'git_group_name', 'git_repo_prefix']
    conf_section = 'Default'


    def __init__(self, config_file, group, exercise, dest_dir, clean_up):
        """

        :param config_file:
        :param group:
        :param exercise:
        :param dest_dir:
        :return:
        """
        self.config_file = config_file
        self.group = group
        self.exercise = exercise
        self.dest_path = '%s%s/' % (dest_dir, exercise)
        self.groups = ''
        self.clean_up = clean_up


    def load_config(self):
        loader = ldr.ConfigLoader(self.config_file)
        config = loader.load_config(self.conf_props, self.conf_section)

        self.url = config['git_url']
        self.groups = config['group_%s' % self.group].split(',')
        self.git_group_name = config['git_group_name']
        self.git_repo_prefix = config['git_repo_prefix']


    def clean(self):
        if os.path.exists(self.dest_path):
            input(Back.RED + Style.BRIGHT + 'This operation will clean the destination directory: {0:s}'.format(
                self.dest_path) + Style.RESET_ALL + '\n' + Back.RED + Style.BRIGHT
                + 'Press <Enter> to continue (CTRL-C to abort):' + Style.RESET_ALL)

            shutil.rmtree(self.dest_path)


    def download(self):
        self.load_config()

        if self.clean_up:
            self.clean()

        for group in self.groups:
            cmd_checkout = 'git clone git@{0:s}:{1:s}/{2:s}{3:s}.git {4:s}{2:s}{3:s}'.format(
                self.url.replace('https://', ''), self.git_group_name, self.git_repo_prefix, group, self.dest_path)
            subprocess.call([cmd_checkout], shell=True)

            cmd_get_tags = 'cd  %s%s%s; git log --tags=%s* --simplify-by-decoration --pretty="format:%%ci %%d"' % ( \
                self.dest_path, self.git_repo_prefix, group, self.exercise)
            subprocess.call([cmd_get_tags], shell=True)

            tag = input('Select tag:')
            cmd_checkout_tag = 'cd  %s%s%s; git checkout tags/%s' % (self.dest_path, self.git_repo_prefix, group, tag)
            subprocess.call([cmd_checkout_tag], shell=True)
