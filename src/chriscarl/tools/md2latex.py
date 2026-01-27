#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Author:         Chris Carl
Email:          chrisbcarl@outlook.com
Date:           2026-01-25
Description:

tools.md2latex is a tool which... TODO: lorem ipsum

Updates:
    2026-01-25 - tools.md2latex - initial commit
'''

# stdlib imports
from __future__ import absolute_import, print_function, division, with_statement  # , unicode_literals
import os
import sys
import logging
from typing import List, Generator, Optional
from dataclasses import dataclass, field
from argparse import ArgumentParser

# third party imports

# project imports
from chriscarl.core.constants import TEMP_DIRPATH
from chriscarl.core.lib.stdlib.logging import NAME_TO_LEVEL, configure_ez
from chriscarl.core.lib.stdlib.argparse import ArgparseNiceFormat
from chriscarl.core.lib.stdlib.os import abspath, make_dirpath
from chriscarl.tools.shed.md2latex import assert_executables_exist

SCRIPT_RELPATH = 'chriscarl/tools/md2latex.py'
if not hasattr(sys, '_MEIPASS'):
    SCRIPT_FILEPATH = os.path.abspath(__file__)
else:
    SCRIPT_FILEPATH = os.path.abspath(os.path.join(sys._MEIPASS, SCRIPT_RELPATH))  # pylint: disable=no-member
SCRIPT_DIRPATH = os.path.dirname(SCRIPT_FILEPATH)
SCRIPT_NAME = os.path.splitext(os.path.basename(__file__))[0]
THIS_MODULE = sys.modules[__name__]
LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())

# argument defaults
DEFAULT_FIB_INIT = [0, 1]
DEFAULT_OUTPUT_DIRPATH = abspath(TEMP_DIRPATH, 'tools.md2latex')
DEFAULT_LOG_FILEPATH = abspath(TEMP_DIRPATH, 'tools.md2latex.log')

# tool constants


@dataclass
class Arguments:
    '''
    Document this class with any specifics for the process function.
    '''
    n: int
    debug: bool
    times: int
    init: List[int] = field(default_factory=lambda: DEFAULT_FIB_INIT)
    output_dirpath: str = DEFAULT_OUTPUT_DIRPATH
    messages: List[str] = field(default_factory=lambda: [])
    log_level: str = 'INFO'
    log_filepath: str = DEFAULT_LOG_FILEPATH

    @staticmethod
    def argparser():
        # type: () -> ArgumentParser
        parser = ArgumentParser(prog=SCRIPT_NAME, description=__doc__, formatter_class=ArgparseNiceFormat)
        app = parser.add_argument_group('app')
        app.add_argument('n', type=int, help='the -th term of fib you want')
        app.add_argument('--times', '-t', type=lambda x: int(x, base=0), required=True, help='print how many times? any numerical format is ok')
        app.add_argument('--init', type=int, nargs=2, default=DEFAULT_FIB_INIT, help='assume sequence starts with these 2 numbers')

        misc = parser.add_argument_group('misc')
        misc.add_argument('--debug', action='store_true', help='chose to print debug info')
        misc.add_argument('--output-dirpath', '-o', type=str, default=DEFAULT_OUTPUT_DIRPATH, help='where do you want to save a text of the sequence')
        misc.add_argument('--messages', '-m', type=str, nargs='*', default=[], help='messages youd like to have printed')
        misc.add_argument('--log-level', type=str, default='INFO', choices=NAME_TO_LEVEL, help='log level?')
        misc.add_argument('--log-filepath', type=str, default=DEFAULT_LOG_FILEPATH, help='log filepath?')
        return parser

    def process(self):
        make_dirpath(self.output_dirpath)
        if self.debug:
            self.log_level = 'DEBUG'
        configure_ez(level=self.log_level, filepath=self.log_filepath)

    @staticmethod
    def parse(parser=None, argv=None):
        # type: (Optional[ArgumentParser], Optional[List[str]]) -> Arguments
        parser = parser or Arguments.argparser()
        ns = parser.parse_args(argv)
        arguments = Arguments(**(vars(ns)))
        arguments.process()
        return arguments


def main():
    # type: () -> int
    parser = Arguments.argparser()
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = Arguments.parse(parser=parser)
    assert_executables_exist()
    print('exist')

    return 0


if __name__ == '__main__':
    sys.exit(main())
'''
Definition:
    - label: a name/label for something ON the doc/bib
    - ref: a reference to a label
    - citation: a ref to a bibliography label

Shape of the algorithm:

# clean the bibliography
    bibliography = read bibliography
    bibtex content = extract bibtex content
    bib-labels = extract all keys
    clean the bibtex content so that it will render correctly
    if any cleaning occurred, copy a new bibfile
    else, use current bibfile
    TODO: test that it renders correctly by doing a dummy documenet

# annotate the markdown
    BAD unicode replace

    sections = []
    header_locations = re.find(#+)
        section.append(pre-amble section is before the first mo)
        sections.extend(ranges from each.)

    errors = []
    doclets = [
        ('yaml', '---asdf: whatever---', spellcheck='')
        ('plain', 'asdfasdfasdf', spellcheck='asdfasdf')
        ('comment', '---asdf: whatever---', spellcheck='')
        ('table', '|||', caption='capt', label='asdf', spellcheck='')
        ...
        ('header', 'introduction', label='introduction', spellcheck='introduction')
        ...
        ('header', 'introduction', label='introduction', spellcheck='introduction', appendix=True)
    ]
    appendix = False
    doc-labels-existing = {}
    doc-refs-requested = []
    for section in sections:
        def analyze_section:
            header? add that to the labels
                if appendix
            errors:
                naked hyperlinks? warn that it must be enclosed
            extract and remove and parse:
                yaml?
            note the range:
                # blocks
                    # may also include refs other blocks or inlines...
                        list?
                        image?
                            path exists, downloaded or downloadable?
                        table?
                            properly captioned, reffed?
                    # cannot include refs
                        comments?
                        latex double?
                        code/backticks?
                # inline
                    backticks?
                    latex single?
                    citations?
                        if interdoc, do they have the pref?

    for ref in doc-refs-requested:
        if ref not in doc-labels-existing:
            add to errors
    if errors:
        ref errors

    yaml = extract yaml section

# wordcount the markdown
    markdown = read markdown
    if wordcount:
        print a best word count and return

# spellcheck if asked

# render the content
    according to yaml
    for doc in doclets
        get latex
    append to body/appendix
'''
