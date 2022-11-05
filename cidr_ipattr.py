#!/usr/bin/env python
#
# IP Address Search Tool
#
# hidekuno@gmail.com
#
class IpAttribute:
    def __init__(self, version):
        if version == 4:
            self.delimiter = '.'
            self.radix = 10
            self.matches = 8
            self.fmt_bin = '08b'
            self.csvfile = 'cidr.txt'
            self.asn_csvfile = 'asn.csv'
        else:
            self.delimiter = ':'
            self.radix = 16
            self.matches = 19
            self.fmt_bin = '016b'
            self.csvfile = 'cidr6.txt'
            self.asn_csvfile = 'asn6.csv'

    def bin_addr(self, ip):
        return "".join([format(int(x, self.radix),self.fmt_bin) for x in ip.exploded.split(self.delimiter)])
