#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Author:         Chris Carl
Email:          chrisbcarl@outlook.com
Date:           2026-01-25
Description:

tools.shed.md2latex is... TODO: lorem ipsum
tool are modules that define usually cli tools or mini applets that I or other people may find interesting or useful.

Updates:
    2026-01-25 - tools.shed.md2latex - initial commit
'''

# stdlib imports
from __future__ import absolute_import, print_function, division, with_statement  # , unicode_literals
import os
import sys
import logging
import re

# third party imports

# project imports
from chriscarl.core.lib.stdlib.subprocess import which

SCRIPT_RELPATH = 'chriscarl/tools/shed/md2latex.py'
if not hasattr(sys, '_MEIPASS'):
    SCRIPT_FILEPATH = os.path.abspath(__file__)
else:
    SCRIPT_FILEPATH = os.path.abspath(os.path.join(sys._MEIPASS, SCRIPT_RELPATH))  # pylint: disable=no-member
SCRIPT_DIRPATH = os.path.dirname(SCRIPT_FILEPATH)
SCRIPT_NAME = os.path.splitext(os.path.basename(__file__))[0]
THIS_MODULE = sys.modules[__name__]
LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())

WIN32 = sys.platform == 'win32'
EXECUTABLES = ['wkhtmltopdf', 'miktex', 'rsvg-convert'] if WIN32 else [] + ['pandoc']


def assert_executables_exist():
    # type: () -> None
    for exe in EXECUTABLES:
        assert which(exe), f'choco install {exe} -y' if WIN32 else 'apt install {} -y'
