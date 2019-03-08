#!/usr/bin/env python3
# -*- coding: utf-8 -*- 
import unittest

# twist import paths so this file can be executed from within my editor in a standard fashion
# for more details see: https://stackoverflow.com/questions/11536764/how-to-fix-attempted-relative-import-in-non-package-even-with-init-py
if __name__ == '__main__' and __package__ is None:
    from os import sys, path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from api import IPU
from config import HOST


######################################################################
#                                                                    #
#      To run these tests create a config.py file as sibling of      #
#    api.py and set the HOST variable to your PDUs IP as a string    #
#                                                                    #
######################################################################


class TestAgainstLiveInstance(unittest.TestCase):
    def setUp(self):
        self.api = IPU(HOST)

    def test_status(self):
        self.assertEqual(
            set(self.api.status().keys()), 
            set(['outlet_states', 'degree_celcius', 'current_amperes', 'humidity_percent', 'stat'])
        )

    def test_outlet_names(self):
        o_names = [('outlet0', 'PACS'), ('outlet1', 'Steckdose2'), 
        ('outlet2', 'Steckdose3'), ('outlet3', 'Steckdose4'), 
        ('outlet4', 'GINA'), ('outlet5', 'GINA Router'), 
        ('outlet6', 'Steckdose7'), ('outlet7', 'UPC Modem')]

        self.assertEqual(self.api.outlet_names(), o_names)

    def test_pdu_config_getter(self):
        resp = self.api.pdu_config()
        for k, v in resp.items():
            self.assertIn('outlet', k)
            self.assertEqual(set(v.keys()), set(['turn_off_delay', 'turn_on_delay', 'name']))

    def test_pdu_config_setter(self):
        push_config = {'outlet1': {'turn_on_delay': 40, 'turn_off_delay': 30, 'name': 'TESTNAME1'}, 
                       'outlet6': {'turn_on_delay': 20, 'turn_off_delay': 10, 'name': 'TEST NAME2'}}
        
        original_config = self.api.pdu_config()
        new_config = self.api.pdu_config(push_config)

        self.assertEqual(new_config['outlet1'], push_config['outlet1'])
        self.assertEqual(new_config['outlet6'], push_config['outlet6'])

        # reset instance
        reset_config = self.api.pdu_config(original_config)
        self.assertEqual(reset_config, original_config)

    def test_get_outlet_states(self):
        self.assertEqual(self.api._get_outlet_states([0, 1, 2, 3, 5, ]), ['on', 'off', 'off', 'off', 'on'])


if __name__ == '__main__':
    unittest.main(exit=False)