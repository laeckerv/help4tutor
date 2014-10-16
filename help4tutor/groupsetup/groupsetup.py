from test.test_contains import seq

__author__ = 'Manuel Hieke'

import gitlab as git
import configloader as ldr
from getpass import *
import logging as log
import groupdictionary

class GroupSetup():
    """
    TODO:

    :author: Manuel Hieke
    """

    conf_props = ['git_url']
    conf_section = 'Default'

    def __init__(self, config_file, src_dir):
        """


        :param src_dir: 
        :param config_file:
        """

        assert isinstance(config_file, basestring)
        self.config_file=config_file
        assert isinstance(src_dir, basestring)
        self.src_dir=src_dir

        loader = ldr.ConfigLoader(self.config_file)
        config = loader.loadConfig(self.conf_props, self.conf_section)

        self.url = config['git_url']
        self.dictAccessor = groupdictionary.GroupDictionary(5)


    def __getToken(self):
        return getpass('Please provide private token from Gitlab (' + self.url + '):')


    def getGitGroups(self):
        gl = git.Gitlab(self.url, self.__getToken(), verify_ssl=True)

        if gl:
            i = 1
            while gl.getprojects(page=i) != []:
                i+=1

