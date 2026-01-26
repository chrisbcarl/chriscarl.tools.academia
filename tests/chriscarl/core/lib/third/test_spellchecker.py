#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Author:         Chris Carl
Email:          chrisbcarl@outlook.com
Date:           2026-01-25
Description:

chriscarl.core.lib.third.spellchecker unit test.

Updates:
    2026-01-25 - tests.chriscarl.core.lib.third.spellchecker - initial commit
'''

# stdlib imports (expected to work)
from __future__ import absolute_import, print_function, division, with_statement  # , unicode_literals
import os
import sys
import logging
import unittest

# third party imports

# project imports (expected to work)
from chriscarl.core import constants
from chriscarl.core.lib.stdlib.os import abspath
from chriscarl.core.lib.stdlib.unittest import UnitTest

# test imports
import chriscarl.core.lib.third.spellchecker as lib

SCRIPT_RELPATH = 'tests/chriscarl/core/lib/third/test_spellchecker.py'
if not hasattr(sys, '_MEIPASS'):
    SCRIPT_FILEPATH = os.path.abspath(__file__)
else:
    SCRIPT_FILEPATH = os.path.abspath(os.path.join(sys._MEIPASS, SCRIPT_RELPATH))  # pylint: disable=no-member
SCRIPT_DIRPATH = os.path.dirname(SCRIPT_FILEPATH)
SCRIPT_NAME = os.path.splitext(os.path.basename(__file__))[0]
THIS_MODULE = sys.modules[__name__]
LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())

constants.fix_constants(lib)  # deal with namespace sharding the files across directories


class TestCase(UnitTest):

    def setUp(self):
        return super().setUp()

    def tearDown(self):
        return super().tearDown()

    # @unittest.skip('lorem ipsum')
    def test_case_0(self):
        lib.load_dictionary()
        self.assertTrue('Wi-Fi' in lib.ACRONYMS)
        self.assertTrue('wi-fi' in lib.DICTIONARY_LOW)
        # variables = [
        #     'OpenAI' in lib.NAMES,
        # ]
        # controls = [
        #     True,
        # ]
        # self.assert_null_hypothesis(variables, controls)

    def test_case_1(self):
        lib.load_dictionary()
        content = '''This will be fuhn.
The 3rd Einstein-Rosen bridge was destroyed.
Aliens from the planet Thessia were the last to ehscape.
'''
        lines = content.splitlines()
        variables = [
            (lib.spellcheck, (content, )),
        ]
        controls = [
            (
                {
                    # error word, lineno, line, recommended replacement
                    'fuhn': [(0, lines[0], 'fun')],
                    'ehscape': [(2, lines[2], 'escape')],
                },
                {
                    # error word, lineno, line, no recommendation to replace
                    'Einstein-Rosen': [(1, lines[1])],
                    'Thessia': [(2, lines[2])],
                },
                # word count approx (3rd doesnt count as a word)
                19
            ),
        ]
        self.assert_null_hypothesis(variables, controls)


if __name__ == '__main__':
    tc = TestCase()
    tc.setUp()

    try:
        tc.test_case_0()
        tc.test_case_1()
    finally:
        tc.tearDown()
