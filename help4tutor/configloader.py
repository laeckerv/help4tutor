import os
import configparser

__author__ = 'mahieke'


class ConfigLoader():
    """
    Class which reads a config file in and check if all parameters
    are given.

    """

    def __init__(self,file):
        """


        :param prop: properties which must exist
        :param file: location of config file
        """
        assert isinstance(file, basestring)
        self.file=file


    @property
    def loadConfig(self, props, section):
        """




        :type props: list
        :param props: List with properties you expect
        :param section: Section of config file
        :return: Dictionary with config
        """
        config = configparser.ConfigParser()
        if os.path.isfile(self.file):
            config.read(self.file)

            if self.__isValidConfig(config[section],props):
                return config


    def __isValidConfig(self, config, props):
        keys = set(sorted(config.keys()))

        if keys.issubset(set(props)):
            return True
        else:
            return False

