#!/usr/bin/env python
#
# IP Address CRUD Rest API
#
# hidekuno@gmail.com
#
from fastapi import FastAPI, Request, Security, Depends, HTTPException
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel, Field
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import text
from sqlalchemy import Column, String, SmallInteger, Integer
from sqlalchemy.exc import IntegrityError
from typing import TypeVar, Generic
from ipaddress import IPv4Address, IPv6Address, IPv4Network, IPv6Network, ip_address, ip_network
import cidr_ipattr


T = TypeVar('T')


def check_api(request: Request,
              api_key: str = Security(APIKeyHeader(name='x-api-key', auto_error=False))):
    safe_clients = ['127.0.0.1', '10.250.10.129', 'testclient']
    API_KEY = 'apitest'

    if (not api_key or api_key != API_KEY):
        raise HTTPException(status_code=401, detail='Invalid or missing API Key')

    # execute fastapi.testclient.TestClient
    if not request.client and not request.headers.get('x-forwarded-for'):
        return

    if (request.client.host not in safe_clients) and (request.headers.get('x-forwarded-for') not in safe_clients):
        raise HTTPException(status_code=403, detail='Forbidden')


class IpGeoModel(BaseModel, Generic[T]):
    cidr: T

    class config:
        orm_mode = True

    def make_dictionary(self, version):
        m = self.model_dump()
        attr = cidr_ipattr.IpAttribute(version)
        net_addr = ip_network(m['cidr'])

        m['cidr'] = str(m['cidr'])
        m['addr'] = attr.bin_addr(net_addr.network_address)
        m['prefixlen'] = net_addr.prefixlen
        return m


class Country(IpGeoModel[T]):
    country: str = Field(..., min_length=2, max_length=2)


class Asn(IpGeoModel[T]):
    asn: int = Field(...)
    provider: str = Field(...)


class City(IpGeoModel[T]):
    city: str = Field(...)


class IpGeo(IpGeoModel[T]):
    country: str = Field(..., min_length=2, max_length=2)
    asn: int = Field(...)
    provider: str = Field(...)
    city: str = Field(...)


Base = declarative_base()


class Ipv4GeoBase:
    addr = Column(String(32), nullable=False, primary_key=True)
    prefixlen = Column(SmallInteger, nullable=False)
    cidr = Column(String(18), nullable=False)


class Ipv6GeoBase:
    addr = Column(String(128), nullable=False, primary_key=True)
    prefixlen = Column(SmallInteger, nullable=False)
    cidr = Column(String(43), nullable=False)


class IPv4CountryTable(Base, Ipv4GeoBase):
    __tablename__ = "ipaddr_v4"

    country = Column(String(2), nullable=False)


class IPv4AsnTable(Base, Ipv4GeoBase):
    __tablename__ = "asn_v4"

    asn = Column(Integer, nullable=False)
    provider = Column(String, nullable=False)


class IPv4CityTable(Base, Ipv4GeoBase):
    __tablename__ = "city_v4"

    city = Column(String, nullable=False)


class IPv6CountryTable(Base, Ipv6GeoBase):
    __tablename__ = "ipaddr_v6"

    country = Column(String(2), nullable=False)


class IPv6AsnTable(Base, Ipv6GeoBase):
    __tablename__ = "asn_v6"

    asn = Column(Integer, nullable=False)
    provider = Column(String, nullable=False)


class IPv6CityTable(Base, Ipv6GeoBase):
    __tablename__ = "city_v6"

    city = Column(String, nullable=False)


def createMySQL():
    user = 'cidr'
    password = 'cidr'
    db_name = 'cidr'
    host = 'db'
    port = 3306

    return create_engine(f'mysql+mysqlconnector://{user}:{password}@{host}:{port}/{db_name}')


CN = TypeVar('CN', IPv4CountryTable, IPv6CountryTable)
ASN = TypeVar('ASN', IPv4AsnTable, IPv6AsnTable)
CITY = TypeVar('CITY', IPv4CityTable, IPv6CityTable)
IPADDRESS = TypeVar('IPADDRESS', IPv4Address, IPv6Address)
IPNETWORK = TypeVar('IPNETWORK', IPv4Network, IPv6Network)


description = """
GeoIP REST API is demo program.

## Ipv4

You can process CRUD for IPV4 regional, ASN, and country.

## Ipv6

You can process CRUD for IPV6 regional, ASN, and country.

"""
app = FastAPI(title="GeoIP REST API",description=description,)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=createMySQL())


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def do_insert(db: Session, record: Base):
    do_insert_multi(db, [record])


def do_insert_multi(db: Session, records: list[Base]):
    try:
        for record in records:
            db.add(record)
        db.commit()
        for record in records:
            db.refresh(record)
    except IntegrityError as e:
        # 23000 is duplicate error of MySQL
        if e.orig.sqlstate == '23000':
            raise HTTPException(status_code=422, detail='Duplicate Error')
        else:
            raise e


def do_delete(db: Session, record: Base):
    do_delete_multi(db, [record])


def do_delete_multi(db: Session, records: list[Base]):
    for record in records:
        db.delete(record)
    db.commit()


def do_update_country(country: Generic[CN], values: dict):
    country.addr = values["addr"]
    country.prefixlen = values["prefixlen"]
    country.cidr = values["cidr"]
    country.country = values["country"]


def do_update_asn(asn: Generic[ASN], values: dict):
    asn.addr = values["addr"]
    asn.prefixlen = values["prefixlen"]
    asn.cidr = values["cidr"]
    asn.asn = values["asn"]
    asn.provider = values["provider"]


def do_update_city(city: Generic[CITY], values: dict):
    city.addr = values["addr"]
    city.prefixlen = values["prefixlen"]
    city.cidr = values["cidr"]
    city.city = values["city"]


def get_ip_records(db: Session, cidr: str, CN, ASN, CITY):
    country = db.query(CN).filter(CN.cidr == cidr).first()
    asn = db.query(ASN).filter(ASN.cidr == cidr).first()
    city = db.query(CITY).filter(CITY.cidr == cidr).first()
    if not country or not asn or not city:
        raise HTTPException(status_code=404, detail="IP not found")

    return (country, asn, city)


def do_all_insert(values: dict, db: Session, CN, ASN, CITY):
    do_insert_multi(
        db,
        [
            CN(
                addr=values["addr"],
                prefixlen=values["prefixlen"],
                cidr=values["cidr"],
                country=values["country"],
            ),
            ASN(
                addr=values["addr"],
                prefixlen=values["prefixlen"],
                cidr=values["cidr"],
                asn=values["asn"],
                provider=values["provider"],
            ),
            CITY(
                addr=values["addr"],
                prefixlen=values["prefixlen"],
                cidr=values["cidr"],
                city=values["city"],
            ),
        ],
    )
    return values


def do_all_update(values: dict, cidr: str, db: Session, CN, ASN, CITY):
    (country, asn, city) = get_ip_records(db, cidr, CN, ASN, CITY)

    do_update_country(country, values)
    do_update_asn(asn, values)
    do_update_city(city, values)

    db.commit()
    return values


def search_query(db: Session, ipaddress: IPADDRESS, version: int):
    query = f"""
    select cidr, country, provider, asn, city
    from
    (select cidr, country from ipaddr_v{version}
     where addr like :param_like and addr like concat(substring(:param,1,prefixlen),'%')) as country,
    (select provider, asn from asn_v{version}
     where addr like :param_like and addr like concat(substring(:param,1,prefixlen),'%')) as asn,
    (select city from city_v{version}
     where addr like :param_like and addr like concat(substring(:param,1,prefixlen),'%')) as city
    """
    attr = cidr_ipattr.IpAttribute(version)
    param = attr.bin_addr(ipaddress)

    ipgeo = (
        db.execute(
            text(query), {"param": param, "param_like": param[: attr.matches] + "%"}
        )
        .mappings()
        .first()
    )
    if not ipgeo:
        raise HTTPException(status_code=404, detail="IP not found")
    return ipgeo


@app.get("/")
def read_root():
    """
    Root endpoint. Returns a simple greeting message.
    """
    return "Hello,World"


@app.get("/ipv4/search")
def read_ipv4(ipv4: IPv4Address, db: Session = Depends(get_db)):
    """
    Searches IPv4 address information.

    - **ipv4**: The IPv4 address.
    """
    return search_query(db, ip_address(ipv4), 4)


@app.post("/ipv4/country", response_model=Country[IPv4Network], dependencies=[Depends(check_api)])
def create_country_ipv4(country: Country[IPv4Network], db: Session = Depends(get_db)):
    """
    Creates a new IPv4 country record.

    - **country**: The country data including CIDR.
    """
    values = country.make_dictionary(4)
    do_insert(db, IPv4CountryTable(**values))
    return values


@app.post("/ipv4/asn", response_model=Asn[IPv4Network], dependencies=[Depends(check_api)])
def create_asn_ipv4(asn: Asn[IPv4Network], db: Session = Depends(get_db)):
    """
    Creates a new IPv4 ASN record.

    - **asn**: The ASN data including CIDR.
    """
    values = asn.make_dictionary(4)
    do_insert(db, IPv4AsnTable(**values))
    return values


@app.post("/ipv4/city", response_model=City[IPv4Network], dependencies=[Depends(check_api)])
def create_city_ipv4(city: City[IPv4Network], db: Session = Depends(get_db)):
    """
    Creates a new IPv4 city record.

    - **city**: The city data including CIDR.
    """
    values = city.make_dictionary(4)
    do_insert(db, IPv4CityTable(**values))
    return values


@app.post("/ipv4", response_model=IpGeo[IPv4Network], dependencies=[Depends(check_api)])
def create_ipv4(ipgeo: IpGeo[IPv4Network], db: Session = Depends(get_db)):
    """
    Creates a new IPv4 record with country, ASN, and city information.

    - **ipgeo**: The IP geolocation data including CIDR.
    """
    return do_all_insert(ipgeo.make_dictionary(4), db, IPv4CountryTable, IPv4AsnTable, IPv4CityTable)


@app.delete("/ipv4", status_code=200, dependencies=[Depends(check_api)])
def delete_ipv4(cidr: IPv4Network, db: Session = Depends(get_db)):
    """
    Deletes an existing IPv4 record.

    - **cidr**: The CIDR of the record to delete.
    """
    do_delete_multi(db, list(get_ip_records(db, str(cidr), IPv4CountryTable, IPv4AsnTable, IPv4CityTable)))
    return "OK"


@app.put("/ipv4", response_model=IpGeo[IPv4Network], dependencies=[Depends(check_api)])
def update_ipv4(cidr: IPv4Network, ipgeo: IpGeo[IPv4Network], db: Session = Depends(get_db)):
    """
    Updates an existing IPv4 record.

    - **cidr**: The CIDR of the record to update.
    - **ipgeo**: The new IP geolocation data.
    """
    return do_all_update(ipgeo.make_dictionary(4), str(cidr), db, IPv4CountryTable, IPv4AsnTable, IPv4CityTable)


@app.get("/ipv6/search")
def read_ipv6(ipv6: IPv6Address, db: Session = Depends(get_db)):
    """
    Searches IPv6 address information.

    - **ipv6**: The IPv6 address to search for.
    """
    return search_query(db, ip_address(ipv6), 6)


@app.post("/ipv6/country", response_model=Country[IPv6Network], dependencies=[Depends(check_api)])
def create_country_ipv6(country: Country[IPv6Network], db: Session = Depends(get_db)):
    """
    Creates a new IPv6 country record.

    - **country**: The country data including CIDR.
    """
    values = country.make_dictionary(6)
    do_insert(db, IPv6CountryTable(**values))
    return values


@app.post("/ipv6/asn", response_model=Asn[IPv6Network], dependencies=[Depends(check_api)])
def create_asn_ipv6(asn: Asn[IPv6Network], db: Session = Depends(get_db)):
    """
    Creates a new IPv6 ASN record.

    - **asn**: The ASN data including CIDR.
    """
    values = asn.make_dictionary(6)
    do_insert(db, IPv6AsnTable(**values))
    return values


@app.post("/ipv6/city", response_model=City[IPv6Network], dependencies=[Depends(check_api)])
def create_city_ipv6(city: City[IPv6Network], db: Session = Depends(get_db)):
    """
    Creates a new IPv6 city record.

    - **city**: The city data including CIDR.
    """
    values = city.make_dictionary(6)
    do_insert(db, IPv6CityTable(**values))
    return values


@app.post("/ipv6", response_model=IpGeo[IPv6Network], dependencies=[Depends(check_api)])
def create_ipv6(ipgeo: IpGeo[IPv6Network], db: Session = Depends(get_db)):
    """
    Creates a new IPv6 record with country, ASN, and city information.

    - **ipgeo**: The IP geolocation data including CIDR.
    """
    return do_all_insert(ipgeo.make_dictionary(6), db, IPv6CountryTable, IPv6AsnTable, IPv6CityTable)


@app.delete("/ipv6", status_code=200, dependencies=[Depends(check_api)])
def delete_ipv6(cidr: IPv6Network, db: Session = Depends(get_db)):
    """
    Deletes an existing IPv6 record.

    - **cidr**: The CIDR of the record to delete.
    """
    do_delete_multi(db, list(get_ip_records(db, str(cidr), IPv6CountryTable, IPv6AsnTable, IPv6CityTable)))
    return "OK"


@app.put("/ipv6", response_model=IpGeo[IPv6Network], dependencies=[Depends(check_api)])
def update_ipv6(cidr: IPv6Network, ipgeo: IpGeo[IPv6Network], db: Session = Depends(get_db)):
    """
    Updates an existing IPv6 record.

    - **cidr**: The CIDR of the record to update.
    - **ipgeo**: The new IP geolocation data.
    """
    return do_all_update(ipgeo.make_dictionary(6), str(cidr), db, IPv6CountryTable, IPv6AsnTable, IPv6CityTable)
