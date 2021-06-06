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
import argparse
import traceback
import ipaddress
import cidr_ipattr

WORK_DIR = os.path.join(os.sep,'tmp')
ZIP_FILENAME = os.path.join(WORK_DIR, 'GeoLite2-Country-CSV.zip')
CSV_URL = 'https://download.maxmind.com/app/geoip_download?edition_id=GeoLite2-Country-CSV&license_key=%s&suffix=zip'
GEOIP_COUNTRY_FILE = 'GeoLite2-Country-Locations-ja.csv'
GEOIP_IP_FILE = 'GeoLite2-Country-Blocks-IPv4.csv'
GEOIP_IPV6_FILE = 'GeoLite2-Country-Blocks-IPv6.csv'

def download_zipfile(args):
    try:
        fd = open(ZIP_FILENAME, 'wb')
        url = urllib.request.urlopen(format(CSV_URL % (args.token)))
        fd.write(url.read())
        fd.close()
        url.close()
    except:
        traceback.print_exc()
        sys.exit(1)

def extract_zipfile():
    coutries = {}
    ipvfile = None
    ipv6file = None
    with zipfile.ZipFile(ZIP_FILENAME,'r') as z:
        for csv in z.namelist():
            base = csv.split('/')[1]
            if base == GEOIP_COUNTRY_FILE:
                z.extract(csv, path=WORK_DIR)
                with codecs.open(os.path.join(WORK_DIR, csv),'r','utf-8') as fd:
                    for line in fd:
                        rec = line.rstrip().split(",")
                        coutries[rec[0]] = rec[4]
            if base == GEOIP_IP_FILE:
                z.extract(csv, path=WORK_DIR)
                ipvfile = os.path.join(WORK_DIR, csv)

            if base == GEOIP_IPV6_FILE:
                z.extract(csv, path=WORK_DIR)
                ipv6file = os.path.join(WORK_DIR, csv)

    if not ipvfile or not ipv6file:
        sys.exit(1)

    return (coutries,ipvfile,ipv6file)

def make_cidr_file(version,coutries,ipvfile):

    attr = cidr_ipattr.IpAttribute(version)
    wfd = codecs.open(os.path.join(os.sep,'tmp',attr.csvfile),'w','utf-8')

    with codecs.open(ipvfile,'r','utf-8') as fd:
        for line in fd:
            rec = line.rstrip().split(",")
            if rec[0][:7] == "network":
                continue

            cidr = ipaddress.ip_network(rec[0])
            naddr = cidr.network_address
            prefix = cidr.prefixlen

            c = rec[2] if rec[2] else rec[1]
            if not c:
                continue
            print(format("%s\t%s\t%s\t%s" % (attr.bin_addr(naddr), prefix, rec[0], coutries[c])), file=wfd)

    wfd.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--token', type=str, dest="token", required=True)
    args = parser.parse_args(sys.argv[1:])
    download_zipfile(args)

    (coutries,ipvfile,ipv6file) = extract_zipfile()
    make_cidr_file(4,coutries,ipvfile)
    make_cidr_file(6,coutries,ipv6file)
