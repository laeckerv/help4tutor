import os

import configparser

__author__ = 'mahieke'


class ConfigLoader():
    """
    Class which reads a config file in and check if all parameters
    are given.

    """

    def __init__(self, file):
        """


        :param prop: properties which must exist
        :param file: location of config file
        """
        try:
            assert isinstance(file, basestring)
        except NameError:
            assert isinstance(file, str)

        self.file = file


    def load_config(self, props, section):
        """

        :type props: list
        :param props: List with properties you expect
        :param section: Section of config file
        :return: Dictionary with config
        """
        config = configparser.ConfigParser()

        if os.path.isfile(self.file):
            config.read(self.file)

            if self.__is_valid_config(config, section, props):
                return config[section]


    def __is_valid_config(self, config, section, props):
        keys = []
        for i in config.options(section):
            keys.append(i)

        if set(props).issubset(set(keys)):
            return True
        else:
            return False
