#!/usr/bin/env python
import os
import sys
import sqlite3
import ipaddress

def eval_ipaddr(ipaddr,cursor):
    ipaddr = ipaddr.strip()

    try:
        ip = ipaddress.IPv4Network(ipaddr)
        if ip.is_private == True:
            return "Private IP address"

    except ValueError:
        return "Not IP address"

    param = "".join([format(int(x),'08b') for x in ipaddr.split('.')])

    stmt = """
    select country, cidr
    from (select addr, country, cidr, subnetmask from ipaddr_v4 where addr like ?)
    where addr like substr(?,1,subnetmask) || ?
    """

    cursor.execute(stmt,tuple([param[:8]+'%', param,'%']))
    row = cursor.fetchone()
    if row:
        return format("%s, %s" % row)
    else:
        return "Not Found"

def repl(cursor):
    print("######## Please Input IP Adress #######\n")

    while True:
        ipaddr = input("<cidr-lite> ")
        if ipaddr == "":
            continue
        if ipaddr == "quit":
            break

        try:
            result = eval_ipaddr(ipaddr,cursor)
            print(result)
        except Exception as e:
            print(e)

if __name__ == "__main__":
    dbpath = os.path.join(os.environ.get("HOME"), "database.cidr")
    try:
        conn = sqlite3.connect(dbpath)
        cursor = conn.cursor()
        cursor.execute("PRAGMA case_sensitive_like=ON;")
        repl(cursor)
        conn.close()

    except Exception as e:
        traceback.print_exc()
        sys.exit(1)
