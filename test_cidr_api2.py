#
# Unit Test Code rest api
#
# pytest -v test_cidr_api2.py
#
from fastapi.testclient import TestClient
from cidr_api2 import app, get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def createMySQL():
    user = 'cidr'
    password = 'cidr'
    db_name = 'cidr'
    host = 'localhost'
    port = 33306

    return create_engine(f'mysql+mysqlconnector://{user}:{password}@{host}:{port}/{db_name}')

TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=createMySQL())

def get_db_test():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = get_db_test

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "Hello": "World",
    }

def test_post_country():
    headers = {
        "x-api-key": "apitest",
        "Content-Type": "application/json",
    }
    json_data = {
        "cidr": "192.168.1.0/24",
        "country": "JP"
    }
    response = client.post("/ipv4/country", headers=headers, json=json_data)
    assert response.status_code == 200
    assert response.json() == {
        "cidr":"192.168.1.0/24",
        "country":"JP",
    }

def test_post_asn():
    headers = {
        "x-api-key": "apitest",
        "Content-Type": "application/json",
    }
    json_data = {
        "cidr": "192.168.1.0/24",
        "asn": 10000,
        "provider": "Mukogawa Net.",
    }
    response = client.post("/ipv4/asn", headers=headers, json=json_data)
    assert response.status_code == 200
    assert response.json() == {
        "cidr":"192.168.1.0/24",
        "asn":10000,
        "provider":"Mukogawa Net.",
    }

def test_post_city():
    headers = {
        "x-api-key": "apitest",
        "Content-Type": "application/json",
    }
    json_data = {
        "cidr": "192.168.1.0/24",
        "city": "兵庫県尼崎市",
    }
    response = client.post("/ipv4/city", headers=headers, json=json_data)
    assert response.status_code == 200
    assert response.json() == {
        "cidr": "192.168.1.0/24",
        "city": "兵庫県尼崎市",
    }

def test_post_all():
    headers = {
        "x-api-key": "apitest",
        "Content-Type": "application/json",
    }
    json_data = {
        "cidr": "192.168.3.0/24",
        "country": "JP",
        "asn": 10001,
        "provider": "Mukogawa2 Net.",
        "city": "兵庫県宝塚市",
    }
    response = client.post("/ipv4", headers=headers, json=json_data)
    assert response.status_code == 200
    assert response.json() == {
        "cidr":"192.168.3.0/24",
        "country":"JP",
        "asn":10001,
        "provider":"Mukogawa2 Net.",
        "city":"兵庫県宝塚市",
    }

def test_put_all():
    headers = {
        "x-api-key": "apitest",
        "Content-Type": "application/json",
    }
    json_data = {
        "cidr": "192.168.3.0/24",
        "country": "JP",
        "asn": 10002,
        "provider": "Mukogawa3 Net.",
        "city": "兵庫県西宮市",
    }
    response = client.put("/ipv4?cidr=192.168.3.0/24", headers=headers, json=json_data)
    assert response.status_code == 200
    assert response.json() == {
        "cidr":"192.168.3.0/24",
        "country":"JP",
        "asn":10002,
        "provider":"Mukogawa3 Net.",
        "city":"兵庫県西宮市",
    }

def test_search():
    response = client.get("/search?ipv4=192.168.1.2")
    assert response.status_code == 200
    assert response.json() == {
        "cidr":"192.168.1.0/24",
        "country":"JP",
        "asn":10000,
        "provider":"Mukogawa Net.",
        "city":"兵庫県尼崎市",
    }
    
    response = client.get("/search?ipv4=192.168.3.2")
    assert response.status_code == 200
    assert response.json() == {
        "cidr":"192.168.3.0/24",
        "country":"JP",
        "asn":10002,
        "provider":"Mukogawa3 Net.",
        "city":"兵庫県西宮市",
    }

def test_delete():
    headers = {
        "x-api-key": "apitest",
    }

    response = client.delete("/ipv4?cidr=192.168.1.0/24", headers=headers)
    assert response.status_code == 200
    assert response.json() == "OK"

    response = client.delete("/ipv4?cidr=192.168.3.0/24", headers=headers)
    assert response.status_code == 200
    assert response.json() == "OK"
