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
python3 cidr_create_geoip.py --token ${your_token}
sqlite3 database.cidr '.read init.sql'
sqlite3 database.cidr '.read city.sql'
```

## Test
```
python3 tests/test_cidr_search.py
```

## Run
```
python3 cidr_search.py
```
- type IP address

![image](https://user-images.githubusercontent.com/22115777/200112280-da0396b6-d4ce-409e-af2d-d014faf19ab2.png)

## Run on docker
### Requirement
- account of maxmind.com(https://www.maxmind.com/en/account/login)
- docker is running.

```
cd ${HOME}
git clone https://github.com/hidekuno/cidr-lite
cd cidr-lite/cli/docker
docker build -t ${yourid}/cidr-lite --file=Dockerfile --build-arg token=${YOUR_TOKEN_ID} .
docker run -it --name cidr-lite ${yourid}/cidr-lite python3 /root/cidr_search.py
```

## fastapi
### Requirement
- fastapi installed.
- uvicorn installed.
- databases installed.
- aiosqlite installed.
- SQLAlchemy installed.
- pydantic installed.

### Run
```
cd ${HOME}/cidr_lite
pip3 install "fastapi[all]"
pip3 install databases
pip3 install aiosqlite

python3 -m uvicorn cidr_api:app --reload
```

### search country,ASN,city
```
curl -v http://localhost:8000/search?ipv4=23.218.95.131
```

## fastapi with MySQL
### Requirement
- docker installed
- fastapi(0.111.0) installed.
- SQLAlchemy installed.
- mysql-connector-python installed.

### Build
```
docker-compose up -d
```

### Test
```
pytest -v tests/test_cidr_api2.py
```
