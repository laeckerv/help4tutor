import gitlab as git
import os
import logging as log
import configparser
from getpass import *


class IssueUploader():
    """
     Class which uploads the content of files [name].md in the src_dir to a
     gitlab server with repositories the name [NAME] as issue. Eg. group1.md
     would be uploaded to repo GROUP1.

    :author: Lars Eckervogt
    """
    def __init__(self, config_file, prefix, exercise, src_dir):
        """

        :param url:
        :param prefix:
        :param exercise:
        :param src_dir:
        :return:
        """

        self.config_file = config_file
        self.prefix = prefix
        self.exercise = exercise
        self.src_dir = src_dir


    def loadConfig(self):
        config = configparser.ConfigParser()
        if os.path.isfile(self.config_file):
            config.read(self.config_file)
        else:
            return FileExistsError

        self.url = config['DEFAULT']['GitlabUrl']

    def getToken(self):
        return getpass('Please provide private token from Gitlab (' + self.url + '):')

    def upload(self):
        self.loadConfig()
        gl = git.Gitlab(self.url, self.getToken(), verify_ssl=False)

        if gl:
            result_files = os.listdir(self.src_dir)
            result_groups = []

            for file in result_files:
                group = file.replace('.md','').upper()
                result_groups.append(group)
                log.info('Added %s to the groups that have a ne result' % group)

            for proj in gl.getprojects(per_page=100):
                if proj['name'] in result_groups:
                    project_id = proj['id']

                    log.info('Found project %s with id %s' % (proj['name'], str(proj['id'])))

                    title = '%s %s' % (self.prefix, self.exercise)
                    label = '%s, %s' % (self.prefix, self.exercise)

                    content = ''
                    with open(self.src_dir + str(proj['name']).lower() + '.md', 'r') as content_file:
                        content = content_file.read()

                    log.info('Creating issue for %s (ID:%s)' % (proj['name'], str(proj['id'])))
                    log.info('\t -> Title: %s ' % title)
                    log.info('\t -> Labels: %s ' % label)

                    input('Press <Enter> to continue (CTRL-C to abort):')

                    gl.createissue(id_=project_id, title=title, description=content, labels=label)