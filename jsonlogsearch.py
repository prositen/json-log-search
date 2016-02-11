import argparse
import fileinput
import json
import sys

__author__ = 'Anna'


def split_to_dict(list_to_split, separator='='):
    """
    Split the strings in a list, and insert into a dictionary.
    Duplicate keys overwrites the previous entries.
    :param list_to_split: list of string
    :param separator: default =
    :return: Dictionary with keys & values from list
    >>> split_to_dict(["a:1", "b:2"], ':')
    {'a': '1', 'b': '2'}
    >>> split_to_dict(["a=1", "b=2"])
    {'a': '1', 'b': '2'}
    >>> split_to_dict(["a=1", "b=2", "a=3"])
    {'a': '3', 'b': '2'}
    >>> split_to_dict(None)
    {}
    >>> sorted(split_to_dict(["a=1", "b", "c=3"]))
    {'a': '1', 'c': '3', 'b': None}
    """
    ret_val = dict()
    if list_to_split:
        for x in list_to_split:
            try:
                key, value = x.split(separator, 1)
            except ValueError:
                key, value = x, None
            ret_val[key] = value
    return ret_val


class JSONSearch(object):
    def squash(self, json_object):
        if isinstance(json_object, dict) and len(json_object) == 1:
            for type in self.parser.types:
                try:
                    return json_object[type]
                except KeyError:
                    pass
        return json_object

    def squash_rec(self, json_object):
        json_object = self.squash(json_object)
        if isinstance(json_object, dict):
            for key, value in json_object.items():
                json_object[key] = self.squash_rec(value)
        return json_object

    def find_rec(self, json_object, value, in_keys, debug=False):
        if isinstance(json_object, dict):
            if in_keys and value in json_object.keys():
                    return True, json_object[value]
            else:
                for json_value in json_object.values():
                    found, child = self.find_rec(json_value, value, in_keys)
                    if found:
                        return True, child
                else:
                    return False, None

        elif isinstance(json_object, list):
            for obj in json_object:
                found, child = self.find_rec(obj, value, in_keys)
                if found:
                    return True, child
            else:
                return False, json_object

        else:
            return str(value) == str(json_object), json_object

    def __init__(self, line, parser):
        self.show = True
        self.json_line = json.loads(line)
        self.parser = parser
        if self.parser.squash:
            self.json_line = self.squash_rec(self.json_line)
        if self.parser.where:
            for where_key, where_value in self.parser.where.items():
                found_key, child = self.find_rec(self.json_line, where_key, True)
                if not found_key:
                    self.show = False
                    break
                else:
                    if where_value is not None:
                        found_value, _dummy = self.find_rec(child, where_value, False)
                        if not found_value:
                            self.show = False
                            break
        if self.parser.where_not:
            for where_key, where_value in self.parser.where_not.items():
                found_key, child = self.find_rec(self.json_line, where_key, True)
                if found_key:
                    if where_value is None:
                        self.show = False
                        break
                    else:
                        if where_value is not None:
                            found_value, _dummy = self.find_rec(child, where_value, False)
                            if found_value:
                                self.show = False
                                break

    def print(self):
        if self.show:
            if self.parser.show:
                found_items = list()
                for i in self.parser.show:
                    found, child = self.find_rec(self.json_line, i, True)
                    if found:
                        if self.parser.csv:
                            found_items.append(str(child))
                        else:
                            found_items.append("{0}={1}".format(i, child))
                print(self.parser.delimiter.join(found_items))
            else:
                print(self.json_line)


class Parser(object):

    def __init__(self, args):
        parser = self.get_arg_parser()
        args = parser.parse_args(args)
        self.where = None
        self.where_not = None
        if args.where:
            self.where = split_to_dict(args.where)
        if args.where_not:
            self.where_not = split_to_dict(args.where_not)
        self.file = args.file
        self.squash = args.squash_typeinfo
        if args.show:
            self.show = args.show
        else:
            self.show = None
        self.types = args.add_type

        self.csv = args.csv
        self.delimiter = '\t'
        if self.csv:
            self.delimiter = ','
        if args.delimiter:
            self.delimiter = args.delimiter

    @staticmethod
    def get_arg_parser():
        parser = argparse.ArgumentParser(description='Search in JSON logs. Expects each log line to be valid JSON.')
        parser.add_argument('--where',
                            help='Filter to lines which contain NAME[=VALUE]',
                            metavar=['FILTER'],
                            nargs='+')
        parser.add_argument('--where-not',
                            help='Filter to lines which do not contain NAME[=VALUE]. Overrides --where.',
                            metavar=['FILTER'],
                            nargs='+')
        parser.add_argument('--dont-squash-typeinfo',
                            help='Don\'t squash json on the form blah : {"int" : 12345} to blah : 12345. '
                                 'Valid types are int, string, array. Default is to squash.  ',
                            action='store_false',
                            default=True,
                            dest='squash_typeinfo')
        parser.add_argument('--add-type',
                            help='Add custom type TYPE to types to squash. ',
                            action='append',
                            default=['int', 'string', 'array'])
        parser.add_argument('--show',
                            help='Show only parameter PARAM in output.',
                            metavar='PARAM',
                            nargs='+')

        parser.add_argument('--delimiter',
                            help='Delimiter between parameters in output, default tab. '
                                 'Only used together with --show parameter')

        parser.add_argument('--csv',
                            help='Parameter names are shown in header only. Delimiter default is changed to comma'
                                 '(can be overridden). Only used together with --show parameter. ',
                            action='store_true')
        parser.add_argument('file', help='Logfile(s)',
                            nargs='*')

        return parser


def main(args):
    parser = Parser(args)
    try:
        if parser.csv:
            print(parser.delimiter)
            print(parser.delimiter.join(parser.show))
        for line in fileinput.input(parser.file, openhook=fileinput.hook_compressed):
            line = JSONSearch(line, parser)
            line.print()
            pass
    except (IOError, KeyboardInterrupt) as e:
        pass

if __name__ == '__main__':
    main(sys.argv[1:])
