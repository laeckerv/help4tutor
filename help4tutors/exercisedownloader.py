import gitlab as git
import configparser
import subprocess
import shutil
import os
from colorama import Fore, Back, Style

class ExerciseDownloader():
    """
    TODO:

    :author: Lars Eckervogt
    """
    def __init__(self, config_file, group, exercise, dest_dir):
        """

        :param config_file:
        :param group:
        :param exercise:
        :param dest_dir:
        :return:
        """

        config = configparser.ConfigParser()
        if os.path.isfile(config_file):
            config.read(config_file)
        else:
            return FileExistsError

        self.url = config['DEFAULT']['gitlaburl']
        self.groups = config['DEFAULT']['group_%s' % group].split(',')
        self.exercise = exercise
        self.dest_dir = '%s%s/' % (dest_dir, exercise)
        self.git_group_name = config['DEFAULT']['git_group_name']
        self.git_repo_prefix = config['DEFAULT']['git_repo_prefix']
        self.clean()

    def clean(self):
        input(Back.RED + Style.BRIGHT + 'This operation will clean the destination directory: %s' % self.dest_dir \
              + Style.RESET_ALL + '\n' \
              + Back.RED + Style.BRIGHT + 'Press <Enter> to continue (CTRL-C to abort):' + Style.RESET_ALL)
        shutil.rmtree(self.dest_dir)

    def download(self):
        for group in self.groups:
            cmd_checkout = 'git clone git@%s:%s%s%s.git %s%s%s' % (self.url.replace('https://', ''), \
                                                                   self.git_group_name, self.git_repo_prefix, group, \
                                                                   self.dest_dir,  self.git_repo_prefix, group)
            subprocess.call([cmd_checkout], shell=True)

            cmd_get_tags = 'cd  %s%s%s; git log --tags=%s* --simplify-by-decoration --pretty="format:%%ci %%d"' % ( \
                                                            self.dest_dir, self.git_repo_prefix, group,self.exercise)
            subprocess.call([cmd_get_tags], shell=True)

            tag = input('Select tag:')
            cmd_checkout_tag = 'cd  %s%s%s; git checkout tags/%s' % (self.dest_dir, self.git_repo_prefix, group,tag)
            subprocess.call([cmd_checkout_tag], shell=True)