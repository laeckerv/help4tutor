__author__ = 'mahieke'

import json
import pprint as p
import colorama

class GroupDictionary():

    def __init__(self, exc=5, maxjoker=3):
        
        assert isinstance(maxjoker, int)
        self.__dict = {u'maxJoker': maxjoker}
        assert isinstance(exc, int)
        self.__exc = exc

        colorama.init(autoreset=True)


    def read_file(self, srcfile):
        assert isinstance(srcfile, str)

        with open(srcfile, 'r') as inp:
            load = json.load(inp)
            self.__dict = load

            firstkey = load.keys()[0]
            first = load[firstkey]
            scndkey = first.keys()[0]

            self.__exc = len(load[firstkey][scndkey]['results'])

        return self.__dict


    def save_in_file(self, dstfile):
        with open(dstfile, 'w') as out:
            json.dump(self.__dict, out, indent=4, separators=(',', ': '))
        print(colorama.Fore.GREEN + u'Group file was saved at {0:s}'.format(dstfile))


    @property
    def get_dict(self):
        return self.__dict


    @property
    def get_groups(self):
        return self.__dict.keys()

    def add_project(self, group, prj, members):
        """

        :param group: Group in lab
        :param prj: Project name
        :param members: list with names of the members
        :return: returns the current dictionary of GroupDictionary
        """
        if self.__dict.has_key(group) == True:
            if not self.__dict[group].has_key(prj):
                new_prj = {prj.decode('UTF-8'): self.__template}

                i=1
                for name in members:
                    new_prj[prj][i] = name.decode('UTF-8')
                    i+=1

                self.__dict[group].update(new_prj)

                return self.__dict


    def add_group(self, group):
        to_add = self.__get_value([group])

        if to_add == None:
            self.__dict[group] = {}
            return self.__dict


    def delete_group(self, group):
        """

        :param group: Group in lab
        """
        to_delete = self.__get_value([group])

        if to_delete != None:
            del to_delete[group]
            return self.__dict


    def delete_project(self, group, prj):
        """

        :param group: Group in lab
        :param prj: Project name
        """
        to_delete = self.__get_value([group,prj])

        if to_delete != None:
            del to_delete[prj]
            return self.__dict


    def edit_result(self, group, prj, lab, percentage):
        """

        :param group: Group in lab
        :param prj: Project name
        :param lab: In which Lab
        :param percentage: percentage for lab
        """
        to_edit = self.__get_value([group,prj,'results',lab])

        if to_edit != None & percentage > 0.0 & percentage < 100.0:
            to_edit[lab] = float(percentage)
            return self.__dict


    def edit_joker(self, group, prj, lab, days):
        """

        :param group: Group in lab
        :param prj: Project name
        :param lab: In which Lab
        :param days: days a team needs as jokerself
        """
        to_edit = self.__get_value([group,prj,'joker', lab])

        if to_edit != None:
            taken_joker = sum(to_edit.values())
            if taken_joker + days <= self.__dict['maxJoker'] & int(days) > 0:
                to_edit[lab] = int(days)
                return self.__dict


    def dismiss_project(self, group, prj):
        to_edit = self.__get_value([group,prj,'dismissed'])

        if to_edit != None:
            to_edit['dismissed'] = True
            return self.__dict


    def un_dismiss_project(self, group, prj):
        to_edit = self.__get_value([group,prj,'dismissed'])

        if to_edit != None:
            to_edit['dismissed'] = False
            return self.__dict

    def __get_value(self, keys):
        my_dict = self.__dict
        result = {}
        check = True

        for key in keys:
            if my_dict.has_key(key):
                result = my_dict
                my_dict = my_dict[key]
            else:
                check = False
                break

        if check == True:
            return result


    @property
    def __template(self):
        results = {}
        joker = {}

        for i in range(1,self.__exc+1):
            results.update({u'L'+str(i): 0.0})
            joker.update({u'L'+str(i): 0})

        return {
            u'results': results,
            u'joker': joker,
            u'dismissed': False,
            u'comments': []
        }