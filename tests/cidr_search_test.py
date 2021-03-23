#!/usr/bin/env python
#
# IP Address Search Tool
#
# hidekuno@gmail.com
#
# Test howto
# 1) python tests/cidr_search_test.py
# 2) cd tests; python -m unittest cidr_search_test
# 3) PYTHONPATH=$HOME/jvn python tests/cidr_search_test.py
#
import unittest
import os
import sqlite3
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))
from cidr_search import eval_ipaddr

class TestMethods(unittest.TestCase):

    # the testing framework will automatically call for every single test
    def setUp(self):
        dbpath = os.path.join(os.environ.get("HOME"), "database.cidr")
        self.conn = sqlite3.connect(dbpath)
        self.cursor = self.conn.cursor()
        self.cursor.execute("PRAGMA case_sensitive_like=ON;")

    # the testing framework will automatically call for every single test
    def tearDown(self):
        self.conn.close()

    # from here testcode
    def test_ipaddr(self):
        r = eval_ipaddr('210.239.78.91',self.cursor)
        self.assertEqual(r, 'JP,210.224.0.0/12')

    def test_ipaddr_private(self):
        try:
            r = eval_ipaddr('192.168.1.1',self.cursor)
        except Exception as e:
            self.assertEqual(str(e), 'Private IP address')

    def test_ipaddr_noip(self):
        try:
            r = eval_ipaddr('999.999.999.999',self.cursor)
        except Exception as e:
            self.assertEqual(str(e), 'Not IP address')

    def test_ipaddr_alphabet(self):
        try:
            r = eval_ipaddr('aaa.bbb.ccc.ddd',self.cursor)
        except Exception as e:
            self.assertEqual(str(e), 'Not IP address')

    def test_ipaddr_notfound(self):
        # class D
        try:
            r = eval_ipaddr('224.1.1.255',self.cursor)
        except Exception as e:
            self.assertEqual(str(e), 'Not Found')

if __name__ == '__main__':
    try:
        unittest.main()

    except Exception as e:
        traceback.print_exc()
        sys.exit(1)
