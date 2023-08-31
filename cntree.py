# ------------------------------------------------------------------------------
# Project : CNTree                                                 /          \
# Filename: cntree.py                                             |     ()     |
# Date    : 08/06/2023                                            |            |
# Author  : cyclopticnerve                                        |   \____/   |
# License : WTFPLv2                                                \          /
# ------------------------------------------------------------------------------

"""
    This module creates a tree of the specified directory, with paths being
    ignored by the filter list and names being formatted according to the
    specified formats.
"""

# NEXT: filter using globs/patterns
# NEXT: list dirs only

# ------------------------------------------------------------------------------
# Imports
# ------------------------------------------------------------------------------

# system imports
import pathlib

# ------------------------------------------------------------------------------
# A class to generate a file tree in text format with the names formatted
# according to a format string
# ------------------------------------------------------------------------------
class CNTree():
    """
        A class to generate a file tree in text format with the names formatted
        according to some format strings

        Methods:
            build_tree(): Creates the new tree and returns its items as a
            string

        This class builds the tree as a complete string, ready to be printed to
        stdout or a file.
    """

    # --------------------------------------------------------------------------
    # Class constants
    # --------------------------------------------------------------------------

    # these are the console/terminal values for the individual
    # prefix/connector chars
    CHAR_VERT       = '\u2502'  # vertical join (pipe)
    CHAR_HORZ       = '\u2500'  # horizontal join (full-width dash)
    CHAR_TEE        = '\u251C'  # tee join (not last item)
    CHAR_ELL        = '\u2514'  # elbow join (last item)
    CHAR_SPACE      = ' '       # single space char

    # these are the preset char sequences for the prefix/connector char sets
    # NB: these must always be equal length
    PREFIX_VERT     = f'{CHAR_VERT}{CHAR_SPACE}'    # next level    ('| ')
    PREFIX_NONE     = f'{CHAR_SPACE}{CHAR_SPACE}'   # skip level    ('  ')
    CONNECTOR_TEE   = f'{CHAR_TEE}{CHAR_HORZ}'      # next sub item ('T-')
    CONNECTOR_ELL   = f'{CHAR_ELL}{CHAR_HORZ}'      # last sub item ('L-')

    # the default directory/file name formats
    FORMAT_NAME     = '$NAME'
    FORMAT_DIR      = f' {FORMAT_NAME}{pathlib.os.sep}'
    FORMAT_FILE     = f' {FORMAT_NAME}'

    # custom error strings
    ERR_NOT_A_DIR   = '"{}" is not a directory'

    # custom sorting order
    SORT_ORDER      = '_.'  # sort first char of name in this order (above ord)

    # --------------------------------------------------------------------------
    # Class methods
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # Initializes the new object
    # --------------------------------------------------------------------------
    def __init__(self):
        """
            Initializes the new object

            Initializes a new instance of the class, setting the default values
            of its properties, and any other code that needs to run to create a
            new object.
        """

        # call super init to initialize the base class
        super().__init__()

        # NB: something i learned the hard way from c++ coding: you want to do
        # AS LITTLE coding in the constructor method because the whole class may
        # not exist at this point! you should definitely not call setter methods
        # on any attrs, as these methods may not exist at the time you call
        # them. so to initialize attrs, set them directly rather than using
        # setter methods.

        # set the initial values of properties
        self._start_dir = None
        self._filter_list = []
        self._dir_format = CNTree.FORMAT_DIR
        self._file_format = CNTree.FORMAT_FILE
        self._root_lead = ''
        self._dir_lead = ''
        self._sort_order = {}
        self._tree = []

    # --------------------------------------------------------------------------
    # Public methods
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # Creates a tree from the given start directory, using filter list,
    # directory and file formats
    # --------------------------------------------------------------------------
    def build_tree(self, start_dir='', filter_list=None, dir_format='',
            file_format=''):
        """
            Creates a tree from the given start directory, using filter list,
            directory and file formats

            Parameters:
                start_dir: The path to the root directory of the tree
                filter_list: A list of directory/file names to filter
                dir_format: The format to use for directories
                file_format: The format to use for files

            Raises:
                OSError: If the start_dir parameter is None or does not contain
                a path to a valid directory

            Returns:
                The current tree as a string

            Creates a tree from the given start directory and filter list, as a
            string.

            Items in the filter list will be skipped. These items should be
            directory or file paths relative to the start directory.
            Example:
                An entry of 'Foo/bar.txt' will skip a file with the absolute
                path '<start dir>/Foo/bar.txt'.
                An entry of 'Foo' (if it points to a directory) will skip a
                directory with the absolute path '<start dir>/Foo/'and
                everything under it.

            The format strings for directory and file names will have the value
            of constant 'CNTree.FORMAT_NAME' (which defaults to '$NAME')
            replaced by the directory or file name.
            Example (assuming CNTree.FORMAT_NAME='$NAME'):
                dir_format = ' [] $NAME'
                item.name = Foo'
                result = ' [] Foo'

            Also, leading spaces in dir_format, when applied to the start_dir
            name, will be left-trimmed to make the tree start at the first
            column.
        """

        # if list is None, create it
        # https://docs.python-guide.org/writing/gotchas/
        if not filter_list:
            filter_list = []

        # reset all props every time this method is called
        self._start_dir = None
        self._filter_list = []
        self._dir_format = CNTree.FORMAT_DIR
        self._file_format = CNTree.FORMAT_FILE
        self._root_lead = ''
        self._dir_lead = ''
        self._sort_order = {}
        self._tree = []

        # sanitize start_dir param
        try:
            self._sanitize_start_dir(start_dir)

        # this exception gets raised if the param=None or the param is not a dir
        except OSError as exception:
            err_string = CNTree.ERR_NOT_A_DIR.format(start_dir)
            raise OSError(err_string) from exception

        # sanitize the filter list
        self._sanitize_filter_list(filter_list)

        # sanitize the format params
        self._sanitize_formats(dir_format, file_format)

        # get leads (extra spaces before prefix/connector)
        self._get_leads()

        # create custom sort dictionary
        self._get_sort_order()

        # add root to tree
        self._add_root()

        # enumerate the start dir and add its contents, starting recursion
        self._add_contents(self._start_dir)

        # turn the final tree array into a string and return it
        return self._get_result()

    # --------------------------------------------------------------------------
    # Private methods
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # Sanitizes the start_dir parameter
    #---------------------------------------------------------------------------
    def _sanitize_start_dir(self, start_dir):
        """
            Sanitizes the start_dir parameter

            Parameters:
                start_dir: The start_dir parameter from build_tree

            Raises:
                OSError: If the start_dir parameter is None or does not contain
                a path to a valid directory

            Ensures the start_dir parameter is a valid path to a directory.
        """

        # check for stupid people (start_dir=None)
        if start_dir is None:
            raise OSError()

        # convert string param to Path object
        self._start_dir = pathlib.Path(start_dir)

        # check for param is not a dir (it happens...)
        if not self._start_dir.is_dir():
            raise OSError()

        # in case the param is relative (replace in-situ)
        self._start_dir = self._start_dir.resolve()

    # --------------------------------------------------------------------------
    # Sanitizes the filter_list parameter
    #---------------------------------------------------------------------------
    def _sanitize_filter_list(self, filter_list):
        """
            Sanitizes the filter_list parameter

            Parameters:
                filter_list: The filter_list parameter from build_tree

            Converts entries in filter_list to absolute pathlib objects relative
            to start_dir.
        """

        # convert all items in filter_list to Path objects
        filter_list = [pathlib.Path(item) for item in filter_list]

        # join anything that's not absolute (should be everything, people...)
        filter_list = [self._start_dir / item if not item.is_absolute()
                else item for item in filter_list]

        # resolve all path objects (gets rid of dots)
        filter_list = [item.resolve() for item in filter_list]

        # set the filter list as the class filter list
        self._filter_list = filter_list

    # --------------------------------------------------------------------------
    # Sanitizes the dir_format and file_format parameters
    #---------------------------------------------------------------------------
    def _sanitize_formats(self, dir_format, file_format):
        """
            Sanitizes the dir_format and file_format parameters

            Parameters:
                dir_format: The format to use for directory names
                file_format: The format to use for file names

            Ensures that the user entered a correctly formatted format string,
            which is to say it includes the CNTree.FORMAT_NAME.
        """

        # set directory/file format
        # NB: make sure the user didn't use an incorrect format value, such as:
        # build_tree(... dir_format=None)
        # or
        # build_tree(..., dir_format='')
        if dir_format and CNTree.FORMAT_NAME in dir_format:
            self._dir_format = dir_format
        if file_format and CNTree.FORMAT_NAME in file_format:
            self._file_format = file_format

    # --------------------------------------------------------------------------
    # Gets the leads (extra spaces) before each entry in the tree
    #---------------------------------------------------------------------------
    def _get_leads(self):
        """
            Gets the leads (extra spaces) before each entry in the tree

            Calculates how many spaces should be presented before each entry in
            the tree. The root folder should have no spaces (left-aligned) and
            each subsequent entry should add the number of spaces in a
            directory's format name. This allows us to align the connector with
            the index of the CNTree.FORMAT_NAME variable.
        """

        # get the leads (extra indents to line up the pipes/tees/ells)
        # NB: we don't care about file leads, nothing goes under a file

        # get the root's format with no leading spaces
        root_fmt = self._dir_format.lstrip()

        # set root lead as string
        root_lead_count = root_fmt.find(CNTree.FORMAT_NAME)
        self._root_lead = ' ' * root_lead_count

        # set directory lead as string
        dir_lead_count = self._dir_format.find(CNTree.FORMAT_NAME)
        self._dir_lead = ' ' * dir_lead_count

    # --------------------------------------------------------------------------
    # Gets the sort order for custom sorting
    #---------------------------------------------------------------------------
    def _get_sort_order(self):
        """
            Gets the sort order for custom sorting

            This just fixes a personal quirk of mine. The default sorting order
            in Python sorts names starting with a dot (.) above a name starting
            with an underscore (_) (as per string.printable), which for me is
            dependant on my locale, en_US, YMMV. THis does not match my IDE,
            Codium, and I want the tree to match my File Explorer in my IDE. So
            to fix this, I created a custom sorter that reverses that. It's not
            really necessary, but it does the job.

            This function creates a dict in the form of:
            {char:index[, char:index, ...]}
            where:
            char(k) is the character in the CNTree.SORT_ORDER string
            index(v) is the ordinal of that char (starting at the lowest
            negative ordinal)
            so that:
            CNTree.SORT_ORDER = '_.'
            results in:
            self._sort_order = {'_': -2, '.': -1}

            most of this came form:
            https://stackoverflow.com/questions/75301122/how-can-i-change-how-python-sort-deals-with-punctuation
        """

        # get length of string to count backwards
        sort_len = len(CNTree.SORT_ORDER)

        # for each char in string
        for index, char in enumerate(CNTree.SORT_ORDER):

            # make a dict entry for the char and it's new ord
            self._sort_order[char] = index - sort_len

    # --------------------------------------------------------------------------
    # Adds the root to the tree
    #---------------------------------------------------------------------------
    def _add_root(self):
        """
            Adds the root to the tree

            This function adds the root item to the tree. It just strips the
            leading blanks to make sure the root is left-aligned.
        """

        # format the root directory name to a display name and add it
        fmt_root = self._dir_format.lstrip()
        rep_name = fmt_root.replace(CNTree.FORMAT_NAME, self._start_dir.name)
        self._tree.append(rep_name)

    # --------------------------------------------------------------------------
    # Enumerates the given directory and adds its contents to the tree
    # --------------------------------------------------------------------------
    def _add_contents(self, item, prefix=''):
        """
            Enumerates the given directory and adds its contents to the tree

            Parameters:
                item: The pathlib object we are adding
                prefix: The current prefix (combination of pipes/blanks) to show
                the level of indentation

            This method is called recursively to build up the visual level of
            indentation, as well as add directory contents to the tree. It does
            a lot of the heavy lifting to determine what gets printed, and how.
        """

        # enum all items in the dir (files and folders) and convert to list
        # NB: we need a list rather than a generator, since we want everything
        # at once (iterdir is a generator, and so yields)
        # this grabs the whole shebang at once
        items = list(item.iterdir())

        # sort everything, first by lowercase name, then by custom sort,
        # then by type (folders first)
        # NB: the item.is_file() might seem backwards, but sort works by placing
        # a false(0) above a true(1), so an item that is NOT a file (ie. a dir,
        # and thus a 0), will be placed above an item that IS a file (and thus a
        # 1)
        items.sort(key=lambda item: str(item).lower())
        items.sort(key=self._do_sort)
        items.sort(key=lambda item: item.is_file())

        # remove the filtered paths
        items = [item for item in items if item not in self._filter_list]

        # get number of files/directories (for determining connector)
        count = len(items)

        # for each entry
        for index, item in enumerate(items):

            # get the type of connector based on position in enum
            connector = (
                CNTree.CONNECTOR_TEE if index < (count - 1)
                    else CNTree.CONNECTOR_ELL
            )

            # get format string based on whether it is a dir or file
            fmt = self._dir_format if item.is_dir() else self._file_format

            # replace name in format string
            rep_name = fmt.replace(CNTree.FORMAT_NAME, item.name)

            # add the item to the tree
            self._tree.append(f'{self._root_lead}{prefix}{connector}{rep_name}')

            # if item is a dir
            if item.is_dir():

                # adjust the prefix, and call _add_contents for the dir
                self._add_dir(item, prefix, count, index)

    # --------------------------------------------------------------------------
    # Creates the final output string of the tree
    #---------------------------------------------------------------------------
    def _get_result(self):
        """
            Creates the final output string of the tree

            Returns:
                The final string representation of the tree

            Gets the internal list representation of the tree, and convert it to
            a string.
        """

        # join the final tree array into a string and return it
        str_out = '\n'.join(self._tree)
        return str_out

    # --------------------------------------------------------------------------
    # Does some extra stuff when adding a directory
    #---------------------------------------------------------------------------
    def _add_dir(self, item, prefix, count, index):
        """
            Does some extra stuff when adding a directory

            Parameters:
                item: The pathlib object to add
                prefix: The prefix for the last pathlib object added
                count: The total number of objects in the parent (for prefix)
                index: The index of this object in its parent (for prefix)

            Does some extra stuff when adding a directory. First, the prefix
            needs to be appended with another pipe or more spaces. Also the line
            needs to account for the directory lead. Then, it needs to recurse
            back to _add_contents.
        """

        # add a vert or a blank
        prefix += (
            CNTree.PREFIX_VERT if index < (count - 1) else CNTree.PREFIX_NONE
        )

        # add some spacing
        prefix += self._dir_lead

        # call _add_contents recursively with current item and new prefix
        self._add_contents(item, prefix)

    # --------------------------------------------------------------------------
    # Sorts items in the item list according to the item name
    # --------------------------------------------------------------------------
    def _do_sort(self, item):
        """
            Sorts items in the item list according to the item name

            Parameters:
                item: The pathlib object to sort

            Returns:
                The index of the sorted item

        """

        # we only sort by the first char of the pathlib object's name
        char = item.name[0]

        # get the ordinal position of the char
        # NB: if the key (char) is present, the get() function returns the value
        # of the specified key. if the key is not present, it returns the second
        # param (the default)
        # Equivalent:
        # if char in self._sort_order.keys():
        #     return self._sort_order[char]
        # else:
        #     return ord(char)
        pos = self._sort_order.get(char, ord(char))

        # get the char's position in the custom sort dict
        return pos

# -)
