# ------------------------------------------------------------------------------
# Project : CNTree                                                 /          \
# Filename: cntree_cli.py                                         |     ()     |
# Date    : 09/02/2023                                            |            |
# Author  : cyclopticnerve                                        |   \____/   |
# License : WTFPLv2                                                \          /
# ------------------------------------------------------------------------------

"""
    This module handles the command line for creating a tree using cntree
"""

# ------------------------------------------------------------------------------
# Imports
# ------------------------------------------------------------------------------

# system imports
import argparse

# local imports
import cntree

# ------------------------------------------------------------------------------
# Constants
# ------------------------------------------------------------------------------

# the description to print in help
__CN_SHORT_DESC__   = \
"""
This program creates a tree of the specified directory, with names being
formatted according to the specified formats, and paths being ignored by the
filter list.
"""

# the version to print in help
__CN_VERSION__      = 'Version 0.0.1'

# a string to combine description and version strings
DV_STR              = f'{__CN_SHORT_DESC__}\n{__CN_VERSION__}'

# print this at the end of help
EPILOG              = \
"""
The format strings for directory and file names will have the value of '$NAME'
replaced by the directory or file name.
Example:
    cntree_cli.py -d " [] $NAME"
    item name = "Foo"
    result = " [] Foo"

Also, leading spaces in the directory format, when applied to the initial
directory, will be left-trimmed to make the name start at the first column.

Items in the filter list will be skipped. These items should be directory or
file paths relative to the start directory.
Example:
    cntree_cli.py -l "Foo/bar.txt,Foo"
    An entry of 'Foo/bar.txt' will skip a file with the absolute path '<start
    dir>/Foo/bar.txt'. An entry of 'Foo' (if it points to a directory) will skip
    a directory with the absolute path '<start dir>/Foo/'and everything under
    it.

-)
"""

# ------------------------------------------------------------------------------
# A dummy class to combine argparse formatters
# ------------------------------------------------------------------------------
class CNFormatter(
    argparse.RawTextHelpFormatter,          # format argument help
    argparse.RawDescriptionHelpFormatter,   # format description/version/epilog
    # argparse.ArgumentDefaultsHelpFormatter, # add default values to arg help
):
    """
        A dummy class to combine argparse formatters
    """

# ------------------------------------------------------------------------------
# This code runs when the file is called from the command line
# ------------------------------------------------------------------------------
if __name__ == '__main__':

    # create parser
    parser = argparse.ArgumentParser(
        description=DV_STR,             # shown in help (-h) and version (-v)
        epilog=EPILOG,                  # shown in help (-h)
        formatter_class=CNFormatter,    # the combined formatters above
    )

    # version arg
    # NB: you should NOT include any other params to add_argument(), as
    # VersionAction will choke on them
    parser.add_argument(
        '-v',
        action='version',
        version=DV_STR,
    )

# -----------------------------------------------------------

    # parser.add_argument(
    #     '-s',                   # what to pass on command line
    #     action='store'
    #     choices=['1', '2'],
    #     const='True',           # value to store if option is flag-only
    #     default='',             # value when not in cmdline (defaults to None)
    #     dest='DEST',            # the prop name in Namespace (not user facing)
    #     # defaults to name of arg, prefer long name, ie 'start_dir' or 's')
    #     help='start_dir help',  # help string (duh)
    #     metavar='start',        # name of value (user facing, used in help)
    #     nargs='?',
    #     required=True,
    #     type='string',
    # )

    # usage: %(prog)s [-o, --option <metavar>] pos

    parser.add_argument(    # positional
        'directory',
        help='the path to the root directory of the tree',
    )

    # dir_format
    parser.add_argument(    # optional
        '-d',
        help='the format string to use for directory names',
        metavar='',
    )

    # file_format
    parser.add_argument(    # optional
        '-f',
        help='the format string to use for file names',
        metavar='',
    )

    # filter_list
    parser.add_argument(    # optional
        '-l',
        help='a list of directory/file names to filter',
        metavar='',
    )

# -----------------------------------------------------------

    args = parser.parse_args()
    # print(args)

# -----------------------------------------------------------

    # we need to convert list param (a string) into a real list
    LIST_FILTER = None
    if args.l:
        LIST_FILTER = args.l.split(',')
        # print(LIST_FILTER)

    tree = cntree.CNTree()

    TREE = tree.build_tree(
        start_dir=args.directory,
        filter_list=LIST_FILTER,
        dir_format=args.d,
        file_format=args.f,
    )

    print(TREE)

# start_dir
#     skip      (nice error), need param
#     none      (not nice, not a dir)
#     ''        (ok, use current)
#     invalid   (not nice, not a dir)
#     full      (ok)
#     rel       (ok)
# filter
#     skip
#     none
#     []
#     dir
#     file
#     dir/file
#     invalid
#     rel
#     abs
# dir_format
#     skip      (ok)
#     none      (ok)
#     ''        (ok)
#     no $NAME  (ok)
# file_format
#     skip
#     none
#     ''
#     no $NAME

# -----------------------------------------------------------

# action
# Specify how an argument should be handled
# 'store', 'store_const', 'store_true', 'append', 'append_const', 'count'
# 'help', 'version'

# choices
# Limit values to a specific set of choices
# ['foo', 'bar'], range(1, 10), or Container instance

# const
# Store a constant value

# default
# Default value used when an argument is not provided
# Defaults to None

# dest
# Specify the attribute name used in the result namespace

# help
# Help message for an argument

# metavar
# Alternate display name for the argument as shown in help

# nargs
# Number of times the argument can be used
# int, '?', '*', or '+'

# required
# Indicate whether an argument is required or optional
# True or False

# type
# Automatically convert an argument to the given type
# int, float, argparse.FileType('w'), or callable function

# -----------------------------------------------------------

# description = DESCRIPTION\nVERSION
# version = DESCRIPTION\nVERSION
# needs RawDescriptionHelpFormatter
