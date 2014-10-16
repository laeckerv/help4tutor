__author__ = 'mahieke'

import json
import pprint as p

class GroupDictionary():

    def __init__(self, exc=5, maxjoker=3):
        
        assert isinstance(maxjoker, int)
        self.__dict = {u'maxJoker': maxjoker}
        assert isinstance(exc, int)
        self.__exc = exc


    def readFile(self, srcfile):
        assert isinstance(srcfile, str)

        with open(srcfile, 'r') as inp:
            load = json.load(inp)
            self.__dict = load

            firstkey = load.keys()[0]
            first = load[firstkey]
            scndkey = first.keys()[0]

            self.__exc = len(load[firstkey][scndkey]['results'])

        return self.__dict


    def saveInFile(self, dstfile):
        with open(dstfile, 'w') as out:
            json.dump(self.__dict, out, indent=4, separators=(',', ': '))
        print(u'Group file was saved at {0:s}'.format(dstfile))


    def addGroup(self, group, prj, members):
        """

        :param group: Group in lab
        :param prj: Project name
        :param members: list with names of the members
        :return: returns the current dictionary of GroupDictionary
        """
        new_group = {prj.decode('UTF-8'): self.__template}

        i=1
        for name in members:
            new_group[prj][i] = name.decode('UTF-8')
            i+=1

        self.__add(self.__dict, group, new_group)

        return self.__dict


    def deleteGroup(self, group):
        """

        :param group: Group in lab
        """
        self.__delete(self.__dict, group)


    def deleteProject(self, group, prj):
        """

        :param group: Group in lab
        :param prj: Project name
        """
        if self.__dict.has_key(group):
            self.__delete(self.__dict[group], prj)


    def editResult(self, group, prj, lab, ):
        """

        :param group: Group in lab
        :param prj: Project name
        :param lab: In which Lab
        """

    def editJoker(self, group, prj, lab):
        """

        :param group:
        :param prj:
        :param lab:
        """

    @staticmethod
    def __add(where, key, value):
        """

        :param where: entrypoint of dicionary
        :param key: key where value should be added
        :param value: value which should be added
        """
        if where.has_key(key):
            if not where[key].has_key(value.keys()[0]):
                where[key].update(value)
        else:
            where[key] = value


    @staticmethod
    def __delete(where, key):
        if where.has_key(key):
            del where[key]


    @property
    def __template(self):
        results = {}
        joker = {}

        for i in range(1,self.__exc+1):
            results.update({u'L'+str(i): ''})
            joker.update({u'L'+str(i): 0})

        return {
            u'results': results,
            u'joker': joker,
            u'dismissed': False,
            u'comments': []
        }