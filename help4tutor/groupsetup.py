__author__ = 'Manuel Hieke'

class GroupSetup():
    def __init__(self, config_file,src_dir):
        """


        :param src_dir: 
        :param config_file:
        """

        assert isinstance(config_file, basestring)
        self.config_file=config_file
        assert isinstance(src_dir, basestring)
        self.src_dir=src_dir
