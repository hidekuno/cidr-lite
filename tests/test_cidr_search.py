#!/usr/bin/env python
#
# IP Address Search Tool
#
# hidekuno@gmail.com
#
# Test howto
# 1) python tests/test_cidr_search.py
# 2) cd tests; python -m unittest test_cidr_search
# 3) PYTHONPATH=$HOME/jvn python tests/test_cidr_search.py
#
import unittest
import traceback
import os
import sqlite3
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))
from cidr_search import *


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
        r = eval_ipaddr("202.232.2.180", self.cursor)
        self.assertEqual(r, "JP,202.224.0.0/11,Internet Initiative Japan Inc.,AS2497")

    def test_ipaddr_private(self):
        try:
            eval_ipaddr("192.168.1.1", self.cursor)
        except Exception as e:
            self.assertEqual(str(e), "Private IP address")

    def test_ipaddr_noip(self):
        try:
            eval_ipaddr("999.999.999.999", self.cursor)
        except Exception as e:
            self.assertEqual(str(e), "Not IP address")

    def test_ipaddr_alphabet(self):
        try:
            eval_ipaddr("aaa.bbb.ccc.ddd", self.cursor)
        except Exception as e:
            self.assertEqual(str(e), "Not IP address")

    def test_ipaddr_multicast(self):
        # class D
        try:
            eval_ipaddr("224.1.1.255", self.cursor)
        except Exception as e:
            self.assertEqual(str(e), "Multicast IP address")

    def test_ipv6addr(self):
        r = eval_ipaddr("2001:240:bb81::10:180", self.cursor)
        self.assertEqual(r, "JP,2001:240::/32,Internet Initiative Japan Inc.,AS2497")

    def test_ipv6addr_linklocal(self):
        try:
            eval_ipaddr("fe80::215:5dff:fe5d:66e9", self.cursor)
        except Exception as e:
            self.assertEqual(str(e), "Private IP address")

    def test_ipv6addr_uniqlocal(self):
        try:
            eval_ipaddr("fc00::215:5dff:fe5d:66e9", self.cursor)
        except Exception as e:
            self.assertEqual(str(e), "Private IP address")

    def test_ipv6addr_multicast(self):
        # class D
        try:
            eval_ipaddr("FF02::1", self.cursor)
        except Exception as e:
            self.assertEqual(str(e), "Multicast IP address")

    def test_ipaddr_city(self):
        if get_city_mode(self.cursor):
            r = eval_ipaddr("202.232.2.180", self.cursor, True)
            self.assertEqual(
                r, "JP,202.224.0.0/11,Internet Initiative Japan Inc.,AS2497,東京都和田"
            )


if __name__ == "__main__":
    try:
        unittest.main()

    except Exception as e:
        print(e, traceback.format_exc(), file=sys.stderr)
        sys.exit(1)
