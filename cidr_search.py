#!/usr/bin/env python
import os
import sys
import sqlite3
import ipaddress

def is_ipaddr(addr):
    try:
        ipaddress.IPv4Network(addr)
        return True
    except ValueError:
        return False


def search(ipaddr):
    try:
        param = "".join([format(int(x),'08b') for x in ipaddr.split('.')])
        stmt="select country, cidr from ipaddr_v4 where addr like substr(?,1,subnetmask) || ?"

        cursor.execute(stmt,tuple([param,'%']))
        row = cursor.fetchone()
        if row:
            print(format("%s, %s" % row))
        else:
            print("Not Found")

    except Exception as e:
        print(e)

def repl():
    print("######## Please Input IP Adress #######\n")

    while True:
        ipaddr = input("<cidr-lite> ")
        if ipaddr == "":
            continue
        if ipaddr == "quit":
            break

        if is_ipaddr(ipaddr) == False:
            print("Not Ipaddress")
            continue

        search(ipaddr)

if __name__ == "__main__":
    dbpath = os.path.join(os.environ.get("HOME"), "database.cidr")
    try:
        conn = sqlite3.connect(dbpath)
        cursor = conn.cursor()
        cursor.execute("PRAGMA case_sensitive_like=ON;")
        repl()
        conn.close()

    except Exception as e:
        traceback.print_exc()
        sys.exit(1)
