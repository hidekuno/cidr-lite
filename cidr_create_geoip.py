#!/usr/bin/env python
#
# IP Address Search Tool
#
# hidekuno@gmail.com
#
import os,os.path
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
CITY_CSV = 'GeoLite2-City-CSV'

GEOIP_COUNTRY_FILE = 'GeoLite2-Country-Locations-ja.csv'
GEOIP_IP_FILE = 'GeoLite2-Country-Blocks-IPv4.csv'
GEOIP_IPV6_FILE = 'GeoLite2-Country-Blocks-IPv6.csv'

GEOIP_ASN_FILE = 'GeoLite2-ASN-Blocks-IPv4.csv'
GEOIP_ASN_IPV6_FILE = 'GeoLite2-ASN-Blocks-IPv6.csv'

GEOIP_CITY_FILE = 'GeoLite2-City-Locations-ja.csv'
GEOIP_CITY_IP_FILE = 'GeoLite2-City-Blocks-IPv4.csv'
GEOIP_CITY_IPV6_FILE = 'GeoLite2-City-Blocks-IPv6.csv'

REGION_GROUP = (GEOIP_COUNTRY_FILE,GEOIP_CITY_FILE,)
IPV4_GROUP = (GEOIP_IP_FILE,GEOIP_ASN_FILE,GEOIP_CITY_IP_FILE,)
IPV6_GROUP = (GEOIP_IPV6_FILE,GEOIP_ASN_IPV6_FILE,GEOIP_CITY_IPV6_FILE,)

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

def extract_zipfile(geofile,obj):
    regions = {}
    ipvfile = None
    ipv6file = None
    zip_filename = os.path.join(WORK_DIR, geofile + '.zip')

    with zipfile.ZipFile(zip_filename,'r') as z:
        for csv_file in z.namelist():
            base = csv_file.split('/')[1]
            if base in REGION_GROUP:
                z.extract(csv_file, path=WORK_DIR)
                with open(os.path.join(WORK_DIR, csv_file),'r') as fd:
                    for line in fd:
                        rec = line.rstrip().split(",")
                        regions[rec[0]] = obj.getName(rec)

            if base in IPV4_GROUP:
                z.extract(csv_file, path=WORK_DIR)
                ipvfile = os.path.join(WORK_DIR, csv_file)

            if base in IPV6_GROUP:
                z.extract(csv_file, path=WORK_DIR)
                ipv6file = os.path.join(WORK_DIR, csv_file)

    if not ipvfile or not ipv6file:
        sys.exit(1)

    return (regions,ipvfile,ipv6file)

def make_cidr_file(version,regions,ipvfile,obj):

    attr = cidr_ipattr.IpAttribute(version)
    wfd = open(os.path.join(os.sep,'tmp',obj.gefCsvName(attr)),'w')

    with open(ipvfile,'r') as fd:
        for line in fd:
            rec = line.rstrip().split(",")
            if rec[0][:7] == "network":
                continue

            cidr = ipaddress.ip_network(rec[0])
            naddr = cidr.network_address
            prefix = cidr.prefixlen

            c = obj.getIdNumber(rec)
            if not c:
                continue
            print(format("%s\t%s\t%s\t%s" % (attr.bin_addr(naddr), prefix, rec[0], regions[c])), file=wfd)

    wfd.close()

def make_asn_file(version,ipvfile):
    attr = cidr_ipattr.IpAttribute(version)
    wfd = open(os.path.join(os.sep,'tmp', attr.asn_csvfile),'w')

    with open(ipvfile,'r') as fd:
        next(csv.reader(fd))
        for r in csv.reader(fd):
            cidr = ipaddress.ip_network(r[0])
            naddr = cidr.network_address
            prefix = cidr.prefixlen

            print("\t".join([attr.bin_addr(naddr), str(prefix)] + r), file=wfd)
    wfd.close()

class Country(object):
    def getName(self,rec):
        return rec[4]

    def getIdNumber(self,rec):
        return rec[2] if rec[2] else rec[1]

    def gefCsvName(self,attr):
        return attr.csvfile

class City(object):
    def getName(self,rec):
        return (rec[7] + rec[10]).replace('"', '')

    def getIdNumber(self,rec):
        return rec[1]

    def gefCsvName(self,attr):
        return attr.city_csvfile

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--token', type=str, dest="token", required=True)
    parser.add_argument('-a','--asn', default=False, action='store_true', required=False)
    parser.add_argument('-c','--country', default=False, action='store_true', required=False)
    parser.add_argument('-C','--city', default=False, action='store_true', required=False)
    args = parser.parse_args(sys.argv[1:])

    all_kind = not args.country and not args.asn and not args.city
    if args.country or all_kind:
        obj = Country()
        download_zipfile(COUNTRY_CSV, args)
        (countries,ipvfile,ipv6file) = extract_zipfile(COUNTRY_CSV,obj)
        make_cidr_file(4,countries,ipvfile,obj)
        make_cidr_file(6,countries,ipv6file,obj)

    if args.asn or all_kind:
        download_zipfile(ASN_CSV, args)
        (_dummy,ipvfile,ipv6file) = extract_zipfile(ASN_CSV,None)
        make_asn_file(4,ipvfile)
        make_asn_file(6,ipv6file)

    if args.city or all_kind:
        obj = City()
        download_zipfile(CITY_CSV, args)
        (citiese,ipvfile,ipv6file) = extract_zipfile(CITY_CSV,obj)
        make_cidr_file(4,citiese,ipvfile,obj)
        make_cidr_file(6,citiese,ipv6file,obj)
