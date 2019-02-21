#!/usr/bin/env python3
# -*- coding: utf-8 -*- 
import unittest
from os import sys, path

# twist import paths so this file can be executed from within my editor in a standard fashion
# for more details see: https://stackoverflow.com/questions/11536764/how-to-fix-attempted-relative-import-in-non-package-even-with-init-py
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from api import IPU
from config import HOST

class TestStringMethods(unittest.TestCase):
    def setUp(self):
        self.api = IPU(HOST)

    def test_status(self):
        self.api.status()


if __name__ == '__main__' and __package__ is None:
    from os import sys, path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    unittest.main()