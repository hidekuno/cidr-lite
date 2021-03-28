IP address search tool
=================

## Overview
- Search the CIDR format network address and country code from the IPv4 address.

## Build
### Requirement
- account of maxmind.com(https://www.maxmind.com/en/account/login)
- python3 installed.
- sqlite3 installed.

```
cd ${HOME}
git clone https://github.com/hidekuno/cidr-lite
cd cidr-lite
python3 cidr_create_geoip.py --token ${your_token} >/tmp/cidr.txt
sqlite3 database.cidr '.read init.sql'
```

## Test
```
python3 tests/cidr_search_test.py
```

## Run
```
python3 cidr_search.py
```
- input ip address 

![image](https://user-images.githubusercontent.com/22115777/112744686-48642880-8fdd-11eb-86c8-357de803f819.png)

## Run on docker
### Requirement
- account of maxmind.com(https://www.maxmind.com/en/account/login)
- docker is running.

```
cd ${HOME}
git clone https://github.com/hidekuno/cidr-lite
cd cidr-lite/docker
docker build -t ${yourid}/cidr-lite --file=Dockerfile --build-arg token=${YOUR_TOKEN_ID} .
docker run -it --name cidr-lite ${yourid}/cidr-lite python3 /root/cidr_search.py
```
![image](https://user-images.githubusercontent.com/22115777/67066250-a798f900-f1ac-11e9-9765-861678a7d32b.png)
