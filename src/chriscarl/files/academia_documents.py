#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Author:         Chris Carl
Email:          chrisbcarl@outlook.com
Date:           2026-02-20
Description:

files.academia_documents is a manifest for all kinds of academia style documents
files are modules that elevate files so they can be used in python, either registering the path name or actually interacting with them like data cabinets.

Updates:
    2026-02-23 - files.academia_documents - added homework.md and notebook.ipynb
    2026-02-20 - files.academia_documents - initial commit
'''

# stdlib imports
from __future__ import absolute_import, print_function, division, with_statement  # , unicode_literals
import os
import sys
import logging

# third party imports

# project imports

SCRIPT_RELPATH = 'chriscarl/files/academia_documents.py'
if not hasattr(sys, '_MEIPASS'):
    SCRIPT_FILEPATH = os.path.abspath(__file__)
else:
    SCRIPT_FILEPATH = os.path.abspath(os.path.join(sys._MEIPASS, SCRIPT_RELPATH))  # pylint: disable=no-member
SCRIPT_DIRPATH = os.path.dirname(SCRIPT_FILEPATH)
SCRIPT_NAME = os.path.splitext(os.path.basename(__file__))[0]
THIS_MODULE = sys.modules[__name__]
LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())

# ###

# ./
DIRPATH_ROOT = SCRIPT_DIRPATH
FILEPATH_ACADEMIA_DOCUMENTS_PY = os.path.join(DIRPATH_ROOT, 'academia_documents.py')

# ./academia
DIRPATH_ACADEMIA = os.path.join(DIRPATH_ROOT, 'academia')
FILEPATH_ACADEMIA_NOTE = os.path.join(DIRPATH_ACADEMIA, './note.md')
FILEPATH_ACADEMIA_LECTURE = os.path.join(DIRPATH_ACADEMIA, './lecture.md')
FILEPATH_ACADEMIA_HOMEWORK = os.path.join(DIRPATH_ACADEMIA, './homework.md')
FILEPATH_ACADEMIA_NOTEBOOK = os.path.join(DIRPATH_ACADEMIA, './notebook.ipynb')
