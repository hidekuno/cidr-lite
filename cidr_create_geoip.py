#!/usr/bin/env python
#
# IP Address Search Tool
#
# hidekuno@gmail.com
#
import os,os.path
import codecs
import sys
import zipfile
import urllib.request

WORK_DIR = os.path.join(os.sep,'tmp')
ZIP_FILENAME = os.path.join(WORK_DIR, 'GeoLite2-Country-CSV.zip')
CSV_URL = 'https://geolite.maxmind.com/download/geoip/database/GeoLite2-Country-CSV.zip'

try:
    fd = open(ZIP_FILENAME, 'wb')
    url = urllib.request.urlopen(CSV_URL)
    fd.write(url.read())
    fd.close()
    url.close()
except:
    traceback.print_exc()    
    sys.exit(1)

coutries = {}
ipvfile = None
with zipfile.ZipFile(ZIP_FILENAME,'r') as z:
    for csv in z.namelist():
        base = csv.split('/')[1]
        if base == 'GeoLite2-Country-Locations-ja.csv':
            z.extract(csv, path=WORK_DIR)
            with codecs.open(os.path.join(WORK_DIR, csv),'r','utf-8') as fd:
                for line in fd:
                    rec = line.rstrip().split(",")
                    coutries[rec[0]] = rec[4]
        if base == 'GeoLite2-Country-Blocks-IPv4.csv':
            z.extract(csv, path=WORK_DIR)
            ipvfile = os.path.join(WORK_DIR, csv)

if not ipvfile:
    sys.exit(1)

with codecs.open(ipvfile,'r','utf-8') as fd:
    for line in fd:
        rec = line.rstrip().split(",")
        cidr = rec[0].split('/')

        if len(cidr) != 2:
            continue
        (ipaddr, mask) = cidr
        bin_addr = "".join([format(int(x),'08b')  for x in ipaddr.split('.')])
        c = rec[2] if rec[2] else rec[1]
        if not c:
            continue
        print(format("%s\t%s\t%s\t%s" % (bin_addr, mask, rec[0], coutries[c])))
