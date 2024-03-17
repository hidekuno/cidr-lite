#
# IP Address Search Rest API
#
# docker run
#
# ex.) curl -X POST -H "x-api-key: apitest" -H "Content-Type: application/json" -d '{"cidr": "192.168.1.0/24", "country": "JP"}' -v http://localhost:8012/ipv4/country
#
# ex.) curl -X POST -H "x-api-key: apitest" -H "Content-Type: application/json" -d '{"cidr": "192.168.1.0/24","asn": 10000, "provider": "Mukogawa Net."}' -v http://localhost:8012/ipv4/asn
#
# ex.) curl -X POST -H "x-api-key: apitest" -H "Content-Type: application/json" -d '{"cidr": "192.168.1.0/24", "city": "兵庫県尼崎市"}' -v http://localhost:8012/ipv4/city
#
# ex.) curl -v http://localhost:8012/search?ipv4=192.168.1.2
#
# ex. curl -X POST -H "x-api-key: apitest" -H "Content-Type: application/json" -d '{"cidr": "192.168.3.0/24", "country": "JP","asn": 10001, "provider": "Mukogawa2 Net.", "city": "兵庫県宝塚市"}' -v http://localhost:8012/ipv4
#
# ex.) curl -v http://localhost:8012/search?ipv4=192.168.3.2
#
# ex.) curl -X PUT -H "x-api-key: apitest" -H "Content-Type: application/json" -d '{"cidr": "192.168.3.0/24", "country": "JP","asn": 10002, "provider": "Mukogawa2 Net.", "city": "兵庫県伊丹市"}' -v http://localhost:8012/ipv4?cidr=192.168.3.0/24
#
# ex.) curl -X DELETE -H "x-api-key: apitest" -v http://localhost:8012/ipv4?cidr=192.168.3.0/24
#
# ex.) curl -v http://localhost:8012/search?ipv4=192.168.3.2
#
# hidekuno@gmail.com
#
from fastapi import FastAPI, Request, Security, Depends, HTTPException
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel, Field, IPvAnyAddress, IPvAnyNetwork
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import text
from sqlalchemy import Column, String, SmallInteger, Integer

import ipaddress
import cidr_ipattr

def check_api(request: Request,
              api_key: str = Security(APIKeyHeader(name='x-api-key', auto_error=False))):
    safe_clients = ['127.0.0.1', '10.250.10.129']
    API_KEY = 'apitest'

    if (not api_key or api_key != API_KEY):
        raise HTTPException(status_code=401, detail='Invalid or missing API Key')

    if (request.client.host not in safe_clients and
        request.headers.get('x-forwarded-for') not in safe_clients):
        raise HTTPException(status_code=403, detail='Forbidden')


class IpGeoModel(BaseModel):
    cidr: IPvAnyNetwork

    class config:
        orm_mode = True

    def make_dictionary(self):
        m = self.dict()
        attr = cidr_ipattr.IpAttribute(4)
        net_addr = ipaddress.ip_network(m['cidr'])

        m['cidr'] = str(m['cidr'])
        m['addr'] = attr.bin_addr(net_addr.network_address)
        m['prefixlen'] = net_addr.prefixlen
        return m


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
    cidr = Column(String(18), nullable=False)


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


def createMySQL():
    user = 'cidr'
    password = 'cidr'
    db_name = 'cidr'
    host = 'db'
    port = 3306

    return create_engine(f'mysql+mysqlconnector://{user}:{password}@{host}:{port}/{db_name}')


app = FastAPI()
engine =  createMySQL()
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
def read_root():
    return {"Hello": "World"}


@app.get("/search")
def read_ipgeo(ipv4: IPvAnyAddress):
    attr = cidr_ipattr.IpAttribute(4)
    param = attr.bin_addr(ipaddress.ip_address(ipv4))

    query = """
    select cidr, country, provider, asn, city
    from
    (select cidr, country from ipaddr_v4 where addr like :param_like and addr like concat(substring(:param,1,prefixlen),'%')) as country,
    (select provider, asn from asn_v4 where addr like :param_like and addr like concat(substring(:param,1,prefixlen),'%')) as asn,
    (select city from city_v4 where addr like :param_like and addr like concat(substring(:param,1,prefixlen),'%')) as city
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


@app.post("/ipv4/country", response_model=Country, dependencies=[Depends(check_api)])
def create_country(country: Country, db: Session = Depends(get_db)):
    values = country.make_dictionary()
    do_insert(db, CountryTable(**values))
    return values


@app.post("/ipv4/asn", response_model=Asn, dependencies=[Depends(check_api)])
def create_asn(asn: Asn, db: Session = Depends(get_db)):
    values = asn.make_dictionary()
    do_insert(db, AsnTable(**values))
    return values


@app.post("/ipv4/city", response_model=City, dependencies=[Depends(check_api)])
def create_city(city: City, db: Session = Depends(get_db)):
    values = city.make_dictionary()
    do_insert(db, CityTable(**values))
    return values


@app.post("/ipv4", response_model=IpGeo, dependencies=[Depends(check_api)])
def create_ipv4(ipgeo: IpGeo, db: Session = Depends(get_db)):
    values = ipgeo.make_dictionary()
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


@app.delete("/ipv4", status_code=201, dependencies=[Depends(check_api)])
def delete_ipv4(cidr: IPvAnyNetwork, db: Session = Depends(get_db)):
    do_delete_multi(db, list(get_ip_records(db, str(cidr))))
    return "OK"


@app.put("/ipv4", response_model=IpGeo, dependencies=[Depends(check_api)])
def update_ipv4(cidr: IPvAnyNetwork, ipgeo: IpGeo, db: Session = Depends(get_db)):
    values = ipgeo.make_dictionary()
    (country, asn, city) = get_ip_records(db, str(cidr))

    do_update_country(country, values)
    do_update_asn(asn, values)
    do_update_city(city, values)

    db.commit()
    return values
