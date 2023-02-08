CREATE TABLE city_v4 (
  addr       char(32),
  prefixlen  smallint,
  cidr       text,
  city       text
);
.separator \t
.import '/tmp/cidr_city.txt' city_v4

CREATE TABLE city_v6 (
  addr       char(128),
  prefixlen  smallint,
  cidr       text,
  city       text
);
.separator \t
.import '/tmp/cidr_city6.txt' city_v6

CREATE INDEX city_v4_idx1 ON city_v4(addr);
CREATE INDEX city_v6_idx1 ON city_v6(addr);
