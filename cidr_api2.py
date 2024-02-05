#
# IP Address Search Rest API
#
# python -m uvicorn cidr_api2:app --reload
#
# ex.) curl -X POST -H "Content-Type: application/json" -d '{"addr": "11000000101010000000000100000000", "prefixlen": 24, "cidr": "192.168.1.0/24", "country": "JP"}' -v http://localhost:8000/ipv4/country
#
# ex.) curl -X POST -H "Content-Type: application/json" -d '{"addr": "11000000101010000000000100000000", "prefixlen": 24, "cidr": "192.168.1.0/24","asn": 10000, "provider": "Mukogawa Net."}' -v http://localhost:8000/ipv4/asn
#
# ex.) curl -X POST -H "Content-Type: application/json" -d '{"addr": "11000000101010000000000100000000", "prefixlen": 24, "cidr": "192.168.1.0/24", "city": "兵庫県尼崎市"}' -v http://localhost:8000/ipv4/city
#
# ex.) curl -v http://localhost:8000/search?ipv4=192.168.1.2
#
# ex. curl -X POST -H "Content-Type: application/json" -d '{"addr": "11000000101010000000001100000000", "prefixlen": 24, "cidr": "192.168.3.0/24", "country": "JP","asn": 10001, "provider": "Mukogawa2 Net.", "city": "兵庫県宝塚市"}' -v http://localhost:8000/ipv4
#
# ex.) curl -v http://localhost:8000/search?ipv4=192.168.3.2
#
# ex.) curl -X DELETE -v http://localhost:8000/ipv4?cidr=192.168.3.0/24
#
# ex.) curl -X PUT -H "Content-Type: application/json" -d '{"addr": "11000000101010000000001100000000", "prefixlen": 24, "cidr": "192.168.3.0/24", "country": "JP","asn": 10002, "provider": "Mukogawa2 Net.", "city": "兵庫県伊丹市"}' -v http://localhost:8000/ipv4?cidr=192.168.3.0/24
#
# curl -v http://localhost:8000/search?ipv4=192.168.3.2
#
# hidekuno@gmail.com
#
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import text
from sqlalchemy import Column, String, SmallInteger, Integer

import os
import ipaddress
from pydantic import IPvAnyAddress,IPvAnyNetwork
import cidr_ipattr


class IpGeoModel(BaseModel):
    addr: str = Field(..., min_length=32, max_length=32)
    prefixlen: int
    cidr: str = Field(..., min_length=9, max_length=18)

    class config:
        orm_mode = True


class Country(IpGeoModel):
    country: str = Field(..., min_length=2, max_length=2)


class Asn(IpGeoModel):
    asn: int = Field(...)
    provider: str = Field(...)


class City(IpGeoModel):
    city: str = Field(...)


class IpGeo(IpGeoModel):
    country: str = Field(..., min_length=2, max_length=2)
    asn: int = Field(...)
    provider: str = Field(...)
    city: str = Field(...)


Base = declarative_base()


class IpGeoBase:
    addr = Column(String(32), nullable=False, primary_key=True)
    prefixlen = Column(SmallInteger, nullable=False)
    cidr = Column(String, nullable=False)


class CountryTable(Base, IpGeoBase):
    __tablename__ = "ipaddr_v4"

    country = Column(String(2), nullable=False)


class AsnTable(Base, IpGeoBase):
    __tablename__ = "asn_v4"

    asn = Column(Integer, nullable=False)
    provider = Column(String, nullable=False)


class CityTable(Base, IpGeoBase):
    __tablename__ = "city_v4"

    city = Column(String, nullable=False)


app = FastAPI()
dbpath = os.path.join(os.environ.get("HOME"), "database.cidr")
engine = create_engine(
    "sqlite:///" + dbpath, connect_args={"check_same_thread": False}, echo=True
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def do_insert(db: Session, record: Base):
    do_insert_multi(db, [record])


def do_insert_multi(db: Session, records: list[Base]):
    for record in records:
        db.add(record)
    db.commit()
    for record in records:
        db.refresh(record)


def do_delete(db: Session, record: Base):
    do_delete_multi(db, [record])


def do_delete_multi(db: Session, records: list[Base]):
    for record in records:
        db.delete(record)
    db.commit()


def do_update_country(country: CountryTable, values: dict):
    country.addr = values["addr"]
    country.prefixlen = values["prefixlen"]
    country.cidr = values["cidr"]
    country.country = values["country"]


def do_update_asn(asn: AsnTable, values: dict):
    asn.addr = values["addr"]
    asn.prefixlen = values["prefixlen"]
    asn.cidr = values["cidr"]
    asn.asn = values["asn"]
    asn.provider = values["provider"]


def do_update_city(city: CityTable, values: dict):
    city.addr = values["addr"]
    city.prefixlen = values["prefixlen"]
    city.cidr = values["cidr"]
    city.city = values["city"]


def get_ip_records(db: Session, cidr: str):
    country = db.query(CountryTable).filter(CountryTable.cidr == cidr).first()
    asn = db.query(AsnTable).filter(AsnTable.cidr == cidr).first()
    city = db.query(CityTable).filter(CityTable.cidr == cidr).first()
    if not country or not asn or not city:
        raise HTTPException(status_code=404, detail="IP not found")

    return (country, asn, city)


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.get("/search")
async def read_ipgeo(ipv4: IPvAnyAddress):
    attr = cidr_ipattr.IpAttribute(4)
    param = attr.bin_addr(ipaddress.ip_address(ipv4))

    query = """
    select cidr, country, provider, asn, city
    from
    (select cidr, country from ipaddr_v4 where addr like :param_like and addr like substr(:param,1,prefixlen) || '%'),
    (select provider, asn from asn_v4 where addr like :param_like and addr like substr(:param,1,prefixlen) || '%'),
    (select city from city_v4 where addr like :param_like and addr like substr(:param,1,prefixlen) || '%')
    """
    ipgeo = (
        engine.execute(
            text(query), {"param": param, "param_like": param[: attr.matches] + "%"}
        )
        .mappings()
        .first()
    )
    if not ipgeo:
        raise HTTPException(status_code=404, detail="Ip not found")
    return ipgeo


@app.post("/ipv4/country", response_model=Country)
async def create_country(country: Country, db: Session = Depends(get_db)):
    values = country.dict()
    do_insert(db, CountryTable(**values))
    return values


@app.post("/ipv4/asn", response_model=Asn)
async def create_asn(asn: Asn, db: Session = Depends(get_db)):
    values = asn.dict()
    do_insert(db, AsnTable(**values))
    return values


@app.post("/ipv4/city", response_model=City)
async def create_city(city: City, db: Session = Depends(get_db)):
    values = city.dict()
    do_insert(db, CityTable(**values))
    return values


@app.post("/ipv4", response_model=IpGeo)
async def create_ipv4(ipgeo: IpGeo, db: Session = Depends(get_db)):
    values = ipgeo.dict()
    do_insert_multi(
        db,
        [
            CountryTable(
                addr=values["addr"],
                prefixlen=values["prefixlen"],
                cidr=values["cidr"],
                country=values["country"],
            ),
            AsnTable(
                addr=values["addr"],
                prefixlen=values["prefixlen"],
                cidr=values["cidr"],
                asn=values["asn"],
                provider=values["provider"],
            ),
            CityTable(
                addr=values["addr"],
                prefixlen=values["prefixlen"],
                cidr=values["cidr"],
                city=values["city"],
            ),
        ],
    )
    return values


@app.delete("/ipv4", status_code=201)
async def delete_ipv4(cidr: IPvAnyNetwork, db: Session = Depends(get_db)):
    do_delete_multi(db, list(get_ip_records(db, str(cidr))))
    return "OK"


@app.put("/ipv4", response_model=IpGeo)
async def update_ipv4(cidr: IPvAnyNetwork, ipgeo: IpGeo, db: Session = Depends(get_db)):
    values = ipgeo.dict()
    (country, asn, city) = get_ip_records(db, str(cidr))

    do_update_country(country, values)
    do_update_asn(asn, values)
    do_update_city(city, values)

    db.commit()
    return values
