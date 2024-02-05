#
# IP Address Search Rest API
#
# python -m uvicorn cidr_api:app --reload
#
# ex.) curl -v http://localhost:8000/search?ipv4=192.168.3.2
#
# hidekuno@gmail.com
#
from fastapi import FastAPI, HTTPException
from databases import Database
import os
import ipaddress
from pydantic import IPvAnyAddress
import cidr_ipattr

app = FastAPI()
dbpath = os.path.join(os.environ.get("HOME"), "database.cidr")
database = Database("sqlite:///" + dbpath)


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


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
    ipgeo = await database.fetch_one(
        query=query, values={"param": param, "param_like": param[: attr.matches] + "%"}
    )
    if not ipgeo:
        raise HTTPException(status_code=404, detail="Ip not found")

    return ipgeo
