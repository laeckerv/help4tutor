import gitlab as git
import os
import logging as log
import help4tutor.configloader as ldr
from help4tutor.utility import get_input as input

from getpass import *


class IssueUploader():
    """
	Class which uploads the content of files [name].md in the src_dir to a
	gitlab server with repositories the name [NAME] as issue. Eg. group1.md
	would be uploaded to repo GROUP1.

	:author: Lars Eckervogt
	"""

    conf_props = ['git_url']
    conf_section = 'Default'

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

        loader = ldr.ConfigLoader(self.config_file)
        config = loader.load_config(self.conf_props, self.conf_section)

        self.url = config['git_url']



    def getToken(self):
        return getpass('Please provide private token from Gitlab (' + self.url + '):')

    def upload(self):

        gl = git.Gitlab(self.url, self.getToken(), verify_ssl=False)

        if gl:
            result_files = os.listdir(self.src_dir)
            result_groups = []

            for file in result_files:
                group = file.replace('.md', '').upper()
                result_groups.append(group)
                log.info('Added %s to the groups that have a ne result' % group)

            ask = True

            for project in gl.getprojects(per_page=100):
                if project['name'] in result_groups:
                    project_id = project['id']

                    log.info('Found project %s with id %s' % (project['name'], str(project['id'])))

                    title = '%s %s' % (self.prefix, self.exercise)
                    label = '%s, %s' % (self.prefix, self.exercise)

                    content = ''
                    with open(self.src_dir + str(project['name']).lower() + '.md', 'r') as content_file:
                        content = content_file.read()

                    log.info('Creating issue for %s (ID:%s)' % (project['name'], str(project['id'])))
                    log.info('\t -> Title: %s ' % title)
                    log.info('\t -> Labels: %s ' % label)

                    if ask:
                        inp = input('Press <Enter> to continue, <c> to not get asked again (CTRL-C to abort):')
                        print(inp)
                        if inp.lower() == 'c':
                            ask = False

                    gl.createissue(id_=project_id, title=title, description=content, labels=label)