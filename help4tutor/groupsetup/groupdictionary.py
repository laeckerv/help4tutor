__author__ = 'mahieke'

import json
import colorama
from tableizer import Tableizer
import math
from collections import OrderedDict

class GroupDictionary():

    def __init__(self, exc=5, maxjoker=3):

        assert isinstance(maxjoker, int)
        self.__dict = {'maxJoker': maxjoker}
        assert isinstance(exc, int)
        self.__exc = exc

        self.__width = 80
        self.__layout_group = [25, 54]

        tmp_width = self.__layout_group[1]
        width_per_lab_col = int(math.floor(tmp_width/(exc)))
        self.__layout_info = [self.__layout_group[0]] + [width_per_lab_col]*(exc)

        colorama.init(autoreset=True)


    def read_file(self, srcfile):
        try:
            assert isinstance(srcfile, basestring)
        except NameError:
            assert isinstance(srcfile, str)

        with open(srcfile, 'r') as inp:
            load = json.load(inp)
            self.__dict = load

            keys = list(load.keys())
            keys.remove('maxJoker')
            firstkey = keys[0]
            first = load[firstkey]
            scndkey = list(first.keys())[0]

            self.__exc = len(load[firstkey][scndkey]['results'])

        return self.__dict


    def save_in_file(self, dstfile):
        with open(dstfile, 'w') as out:
            json.dump(self.__dict, out, indent=4, separators=(',', ': '))
        print(colorama.Fore.GREEN + u'Group file was saved at {0:s}'.format(dstfile))


    @property
    def get_dict(self):
        return self.__dict


    def get_groups(self):
        keys = list(self.__dict.keys())
        keys.remove('maxJoker')
        return keys


    def add_project(self, group, prj, members):
        """

        :param group: Group in lab
        :param prj: Project name
        :param members: list with names of the members
        :return: returns the current dictionary of GroupDictionary
        """
        if group in self.__dict:
            if prj not in self.__dict[group]:
                new_prj = {prj: self.__template}

                new_prj[prj]['members'] = members

                self.__dict[group].update(new_prj)

                return self.__dict


    def add_group(self, group):
        to_add = self.__get_value([group])

        if not to_add:
            self.__dict[group] = {}
            return self.__dict


    def delete_group(self, group):
        """

        :param group: Group in lab
        """
        to_delete = self.__get_value([group])

        if to_delete:
            del to_delete[group]
            return self.__dict


    def delete_project(self, prj):
        """

        :param prj: Project name
        """
        group = self.__get_group(prj)
        to_delete = self.__get_value([group, prj])

        if to_delete:
            del to_delete[prj]
            return self.__dict


    def edit_result(self, prj, lab, percentage):
        """

        :param prj: Project name
        :param lab: In which Lab
        :param percentage: percentage for lab
        """
        group = self.__get_group(prj)
        to_edit = self.__get_value([group, prj, 'results', lab])

        if to_edit and 0.0 <= float(percentage) <= 100.0:
            to_edit[lab] = float(percentage)
            return self.__dict


    def edit_joker(self, prj, lab, days):
        """

        :param prj: Project name
        :param lab: In which Lab
        :param days: days a team needs as jokerself
        """
        group = self.__get_group(prj)
        to_edit = self.__get_value([group, prj, 'joker', lab])

        if to_edit != None:
            taken_joker = sum(to_edit.values()) - to_edit[lab]
            if taken_joker + int(days) <= self.__dict['maxJoker'] and int(days) > 0:
                to_edit[lab] = int(days)
                return self.__dict


    def dismiss_project(self, prj):
        group = self.__get_group(prj)
        to_edit = self.__get_value([group, prj, 'dismissed'])

        if to_edit:
            to_edit['dismissed'] = True
            return self.__dict


    def un_dismiss_project(self, prj):
        group = self.__get_group(prj)
        to_edit = self.__get_value([group,prj,'dismissed'])

        if to_edit != None:
            to_edit['dismissed'] = False
            return self.__dict


    def get_project_groups(self, selector):
        '''

        :param selector:
        :return: None or list with all groupnames
        '''
        try:
            if not isinstance(selector, basestring):
                raise TypeError('selector must be a valid string')
        except NameError:
            if not isinstance(selector, str):
                raise TypeError('selector must be a valid string')

        ret_val = []

        if selector == 'all':
            ret_val = sorted(sum([list(self.__dict[x].keys()) for x in self.get_groups()], []))
        elif selector in self.get_groups():
            ret_val = sorted(self.__dict[selector].keys())

        return ret_val


    def print_groups_overview(self):
        self.__pprint_projects(self.get_groups())


    def print_groups(self, group_name):
        if group_name and not isinstance(group_name, str):
            raise TypeError('parameter group_name must be of type str')

        if group_name and group_name not in self.get_groups():
                raise ValueError('Specified group name is not in member file.')

        if group_name:
            self.__pprint_projects([group_name], True)
        else:
            self.__pprint_projects(self.get_groups(), True)

    def print_project(self,project):
        group = self.__get_group(project)
        if group:
            tbl = Tableizer(self.__width)
            self.__pprint_project(tbl,group,project,True)
            tbl.print_table()
        else:
            raise ValueError('Project "' + project + '" does not exist.')

    def __pprint_projects(self, groups, more=False):
        tbl = Tableizer(self.__width)
        for k in sorted(groups):
            tbl.next_layout([self.__width])
            tbl.add_row(['Group ' + k +':'], colorama.Back.WHITE + colorama.Fore.BLACK + colorama.Style.NORMAL)
            for proj in sorted(list(self.__dict[k].keys()), key=lambda t: int(t.split('_')[2])):
                self.__pprint_project(tbl,k,proj,more)
                tbl.next_layout([self.__width])
                tbl.add_row(['-'*(self.__width-1)], colorama.Back.WHITE + colorama.Fore.BLACK + colorama.Style.NORMAL)
                tbl.next_layout(self.__layout_group)

            tbl.add_seperator(colorama.Back.BLACK)

        tbl.print_table()


    def __pprint_project(self, tbl, group, proj, more=False):
        tbl.next_layout(self.__layout_group)
        dismissed = ''
        back = colorama.Back.WHITE
        if self.__dict[group][proj]['dismissed']:
            dismissed = '     (DISMISSED)'
            back = colorama.Back.RED


        tbl.add_row(['Project name', 'Members' + dismissed], back + colorama.Fore.BLACK + colorama.Style.BRIGHT)

        first_member = True
        for member in self.__dict[group][proj]['members']:
            if first_member:
                first_member = False
                tbl.add_row([proj,member], back + colorama.Fore.BLACK + colorama.Style.NORMAL)
            else:
                tbl.add_rrow([member], back + colorama.Fore.BLACK + colorama.Style.NORMAL)

        if more:
            tbl.next_layout(self.__layout_info)
            results = OrderedDict(sorted(self.__dict[group][proj]['results'].items()))
            jokers = OrderedDict(sorted(self.__dict[group][proj]['joker'].items()))

            tbl.add_rrow(list(results.keys()), back + colorama.Fore.BLACK + colorama.Style.BRIGHT)
            tbl.add_row(['results:'] + list(results.values()), back + colorama.Fore.BLACK + colorama.Style.NORMAL)
            tbl.add_row(['joker:'] + list(jokers.values()), back + colorama.Fore.BLACK + colorama.Style.NORMAL)


    def __get_group(self, project):
        ret_val = ''
        for next_parent in self.get_groups():
            if project in list(self.__dict[next_parent].keys()):
                ret_val = next_parent
                return ret_val


    def __get_value(self, keys):
        my_dict = self.__dict
        result = {}
        check = True

        for key in keys:
            if key in my_dict:
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
            results.update({'L'+str(i): 0.0})
            joker.update({'L'+str(i): 0})

        return {
            'results': results,
            'joker': joker,
            'dismissed': False,
            'comments': []
        }

