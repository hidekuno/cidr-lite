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
import csv

WORK_DIR = os.path.join(os.sep,'tmp')
CSV_URL = 'https://download.maxmind.com/app/geoip_download?edition_id=%s&license_key=%s&suffix=zip'
COUNTRY_CSV = 'GeoLite2-Country-CSV'
ASN_CSV = 'GeoLite2-ASN-CSV'

GEOIP_COUNTRY_FILE = 'GeoLite2-Country-Locations-ja.csv'
GEOIP_IP_FILE = 'GeoLite2-Country-Blocks-IPv4.csv'
GEOIP_IPV6_FILE = 'GeoLite2-Country-Blocks-IPv6.csv'

GEOIP_ASN_FILE = 'GeoLite2-ASN-Blocks-IPv4.csv'
GEOIP_ASN_IPV6_FILE = 'GeoLite2-ASN-Blocks-IPv6.csv'

def download_zipfile(geofile,args):
    try:
        zip_filename = os.path.join(WORK_DIR, geofile + '.zip')
        fd = open(zip_filename, 'wb')
        url = urllib.request.urlopen(format(CSV_URL % (geofile, args.token)))
        fd.write(url.read())
        fd.close()
        url.close()
    except:
        traceback.print_exc()
        sys.exit(1)

def extract_zipfile(geofile):
    countries = {}
    ipvfile = None
    ipv6file = None
    zip_filename = os.path.join(WORK_DIR, geofile + '.zip')

    with zipfile.ZipFile(zip_filename,'r') as z:
        for csv in z.namelist():
            base = csv.split('/')[1]
            if base == GEOIP_COUNTRY_FILE:
                z.extract(csv, path=WORK_DIR)
                with codecs.open(os.path.join(WORK_DIR, csv),'r','utf-8') as fd:
                    for line in fd:
                        rec = line.rstrip().split(",")
                        countries[rec[0]] = rec[4]
            if base in [GEOIP_IP_FILE, GEOIP_ASN_FILE]:
                z.extract(csv, path=WORK_DIR)
                ipvfile = os.path.join(WORK_DIR, csv)

            if base in [GEOIP_IPV6_FILE, GEOIP_ASN_IPV6_FILE]:
                z.extract(csv, path=WORK_DIR)
                ipv6file = os.path.join(WORK_DIR, csv)

    if not ipvfile or not ipv6file:
        sys.exit(1)

    return (countries,ipvfile,ipv6file)

def make_cidr_file(version,countries,ipvfile):

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
            print(format("%s\t%s\t%s\t%s" % (attr.bin_addr(naddr), prefix, rec[0], countries[c])), file=wfd)

    wfd.close()

def make_asn_file(version,ipvfile):
    attr = cidr_ipattr.IpAttribute(version)
    wfd = codecs.open(os.path.join(os.sep,'tmp', attr.asn_csvfile),'w','utf-8')

    with codecs.open(ipvfile,'r','utf-8') as fd:
        next(csv.reader(fd))
        for r in csv.reader(fd):
            cidr = ipaddress.ip_network(r[0])
            naddr = cidr.network_address
            prefix = cidr.prefixlen

            print("\t".join([attr.bin_addr(naddr), str(prefix)] + r), file=wfd)
    wfd.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--token', type=str, dest="token", required=True)
    parser.add_argument('-a','--asn', default=False, action='store_true', required=False)
    parser.add_argument('-c','--country', default=False, action='store_true', required=False)
    args = parser.parse_args(sys.argv[1:])

    both = not args.country and not args.asn
    if args.country or both:
        download_zipfile(COUNTRY_CSV, args)
        (countries,ipvfile,ipv6file) = extract_zipfile(COUNTRY_CSV)
        make_cidr_file(4,countries,ipvfile)
        make_cidr_file(6,countries,ipv6file)
    if args.asn or both:
        download_zipfile(ASN_CSV, args)
        (countries,ipvfile,ipv6file) = extract_zipfile(ASN_CSV)
        make_asn_file(4,ipvfile)
        make_asn_file(6,ipv6file)
