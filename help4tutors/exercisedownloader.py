import gitlab as git
from getpass import *
import os

class ExerciseDownloader():
    """

    """
    def __init__(self, url,  groups, exercise, dest_dir):
        """

        :param url:
        :param token:
        :param groups:
        :param excercise:
        :param checkout_dir:
        :return:
        """

        self.url = url
        self.groups = groups
        self.exercise = exercise
        self.dest_dir = dest_dir

    def download(self):
        """

        :return:
        """
        # TODO:
