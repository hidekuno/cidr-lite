CREATE TABLE ipaddr_v4 (
  addr       char(32),
  prefixlen  smallint,
  cidr       text,
  country    char(2)
);
.separator \t
.import '/tmp/cidr.txt' ipaddr_v4

CREATE TABLE ipaddr_v6 (
  addr       char(128),
  prefixlen  smallint,
  cidr       text,
  country    char(2)
);
.separator \t
.import '/tmp/cidr6.txt' ipaddr_v6

CREATE INDEX ipaddr_v4_idx1 ON ipaddr_v4(addr);
CREATE INDEX ipaddr_v6_idx1 ON ipaddr_v6(addr);

CREATE TABLE asn_v4 (
  addr       char(32),
  prefixlen  smallint,
  cidr       text,
  asn        int,
  provider   text
);
.separator \t
.import '/tmp/asn.csv' asn_v4

CREATE TABLE asn_v6 (
  addr       char(128),
  prefixlen  smallint,
  cidr       text,
  asn        int,
  provider   text
);
.separator \t
.import '/tmp/asn6.csv' asn_v6

CREATE INDEX asn_v4_idx1 ON asn_v4(addr);
CREATE INDEX asn_v6_idx1 ON asn_v6(addr);
