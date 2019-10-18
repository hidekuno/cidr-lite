CREATE TABLE ipaddr_v4 (
  addr       char(32),
  subnetmask smallint,
  cidr       text,
  country    char(2)
);
.separator \t
.import '/root/cidr.txt' ipaddr_v4

CREATE INDEX ipaddr_v4_idx1 ON ipaddr_v4(addr);
