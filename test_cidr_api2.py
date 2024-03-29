#
# Unit Test Code rest api
#
# pytest -v test_cidr_api2.py
#
from fastapi.testclient import TestClient
from cidr_api2 import app, get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import copy

HEADERS = {
    "x-api-key": "apitest",
    "Content-Type": "application/json",
}

def make_assert_data(json_data, method, uri):
    def assert_body(typ, **kwargs):
        test_json_data = json_data.copy()

        for k in ["cidr", "country", "asn", "provider", "city",]:
            v = kwargs.get(k)
            if v:
                test_json_data[k] = v
                break

        response = method(uri, headers=HEADERS, json=test_json_data)
        assert response.status_code == 422
        assert response.json()["detail"][0]["type"] == typ

    return assert_body


def createMySQL():
    user = "cidr"
    password = "cidr"
    db_name = "cidr"
    host = "localhost"
    port = 33306

    return create_engine(
        f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{db_name}"
    )


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
    assert response.json() == "Hello,World"


def test_post_country():
    json_data = {"cidr": "192.168.1.0/24", "country": "JP"}
    response = client.post("/ipv4/country", headers=HEADERS, json=json_data)
    assert response.status_code == 200
    assert response.json() == {
        "cidr": "192.168.1.0/24",
        "country": "JP",
    }


def test_post_asn():
    json_data = {
        "cidr": "192.168.1.0/24",
        "asn": 10000,
        "provider": "Mukogawa Net.",
    }
    response = client.post("/ipv4/asn", headers=HEADERS, json=json_data)
    assert response.status_code == 200
    assert response.json() == {
        "cidr": "192.168.1.0/24",
        "asn": 10000,
        "provider": "Mukogawa Net.",
    }


def test_post_city():
    json_data = {
        "cidr": "192.168.1.0/24",
        "city": "兵庫県尼崎市",
    }
    response = client.post("/ipv4/city", headers=HEADERS, json=json_data)
    assert response.status_code == 200
    assert response.json() == {
        "cidr": "192.168.1.0/24",
        "city": "兵庫県尼崎市",
    }


def test_post_all():
    json_data = {
        "cidr": "192.168.3.0/24",
        "country": "JP",
        "asn": 10001,
        "provider": "Mukogawa2 Net.",
        "city": "兵庫県宝塚市",
    }
    response = client.post("/ipv4", headers=HEADERS, json=json_data)
    assert response.status_code == 200
    assert response.json() == {
        "cidr": "192.168.3.0/24",
        "country": "JP",
        "asn": 10001,
        "provider": "Mukogawa2 Net.",
        "city": "兵庫県宝塚市",
    }


def test_put_all():
    json_data = {
        "cidr": "192.168.3.0/24",
        "country": "JP",
        "asn": 10002,
        "provider": "Mukogawa3 Net.",
        "city": "兵庫県西宮市",
    }
    response = client.put("/ipv4?cidr=192.168.3.0/24", headers=HEADERS, json=json_data)
    assert response.status_code == 200
    assert response.json() == {
        "cidr": "192.168.3.0/24",
        "country": "JP",
        "asn": 10002,
        "provider": "Mukogawa3 Net.",
        "city": "兵庫県西宮市",
    }


def test_search():
    response = client.get("/search?ipv4=192.168.1.2")
    assert response.status_code == 200
    assert response.json() == {
        "cidr": "192.168.1.0/24",
        "country": "JP",
        "asn": 10000,
        "provider": "Mukogawa Net.",
        "city": "兵庫県尼崎市",
    }

    response = client.get("/search?ipv4=192.168.3.2")
    assert response.status_code == 200
    assert response.json() == {
        "cidr": "192.168.3.0/24",
        "country": "JP",
        "asn": 10002,
        "provider": "Mukogawa3 Net.",
        "city": "兵庫県西宮市",
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


def test_error_post_country():
    json_data = {"cidr": "192.168.1.0/24", "country": "JP"}
    assert_body = make_assert_data(json_data, client.post, "/ipv4/country")
    assert_body("ip_any_network", cidr="a.a.a.a")
    assert_body("string_too_short", country="J")
    assert_body("string_too_long", country="JP1")
    assert_body("string_type", country=10)


def test_error_post_asn():
    json_data = {
        "cidr": "192.168.1.0/24",
        "asn": 10000,
        "provider": "Mukogawa Net.",
    }
    assert_body = make_assert_data(json_data, client.post, "/ipv4/asn")
    assert_body("ip_any_network", cidr="a.a.a.a")
    assert_body("int_parsing", asn="a")
    assert_body("string_type", provider=10)


def test_error_post_city():
    json_data = {
        "cidr": "192.168.1.0/24",
        "city": "兵庫県尼崎市",
    }
    assert_body = make_assert_data(json_data, client.post, "/ipv4/city")
    assert_body("ip_any_network", cidr="a.a.a.a")
    assert_body("string_type", city=10)


def test_error_post_all():
    json_data = {
        "cidr": "192.168.3.0/24",
        "country": "JP",
        "asn": 10002,
        "provider": "Mukogawa3 Net.",
        "city": "兵庫県芦屋市",
    }

    assert_body = make_assert_data(json_data, client.post, "/ipv4")
    assert_body("ip_any_network", cidr="a.a.a.a")
    assert_body("string_too_short", country="J")
    assert_body("string_too_long", country="JP1")
    assert_body("string_type", country=10)
    assert_body("int_parsing", asn="a")
    assert_body("string_type", provider=10)
    assert_body("string_type", city=10)

    response = client.post("/ipv4", headers=HEADERS, json=json_data)
    assert response.status_code == 200

    response = client.post("/ipv4", headers=HEADERS, json=json_data)
    assert response.status_code == 422
    assert response.json() == { "detail": "Duplicate Error", }

    response = client.delete("/ipv4?cidr=192.168.3.0/24", headers={ "x-api-key": "apitest",})
    assert response.status_code == 200

def test_error_put_all():
    response = client.put("/ipv4?cidr=192.168.3.0/24", headers=HEADERS)
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "input": None,
                "loc": [
                    "body",
                ],
                "msg": "Field required",
                "type": "missing",
                "url": "https://errors.pydantic.dev/2.5/v/missing",
            },
        ],
    }

    json_data = {
        "cidr": "192.168.3.0/24",
        "country": "JP",
        "asn": 10002,
        "provider": "Mukogawa3 Net.",
        "city": "兵庫県芦屋市",
    }
    assert_body = make_assert_data(json_data, client.put, "/ipv4?cidr=a.a.a.a")
    assert_body("ip_any_network")

    assert_body = make_assert_data(json_data, client.put, "/ipv4?cidr=192.168.3.0/24")
    assert_body("ip_any_network", cidr="a.a.a.a")
    assert_body("string_too_short", country="J")
    assert_body("string_too_long", country="JP1")
    assert_body("string_type", country=10)
    assert_body("int_parsing", asn="a")
    assert_body("string_type", provider=10)
    assert_body("string_type", city=10)


def test_error_search():
    response = client.get("/search?ipv4=a.a.a.a")
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "type": "ip_any_address",
                "loc": ["query", "ipv4"],
                "msg": "value is not a valid IPv4 or IPv6 address",
                "input": "a.a.a.a",
            }
        ]
    }
    response = client.get("/search")
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "type": "missing",
                "loc": ["query", "ipv4"],
                "msg": "Field required",
                "input": None,
                "url": "https://errors.pydantic.dev/2.5/v/missing",
            }
        ]
    }
    response = client.get("/search?ipv4=172.17.0.11")
    assert response.status_code == 404
    assert response.json() == {
        "detail": "IP not found",
    }


def test_error_delete():
    headers = {
        "x-api-key": "apitest",
    }
    response = client.delete("/ipv4?cidr=a.a.a.a", headers=headers)
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "type": "ip_any_network",
                "loc": ["query", "cidr"],
                "msg": "value is not a valid IPv4 or IPv6 network",
                "input": "a.a.a.a",
            }
        ]
    }
    response = client.delete("/ipv4", headers=headers)
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "type": "missing",
                "loc": ["query", "cidr"],
                "msg": "Field required",
                "input": None,
                "url": "https://errors.pydantic.dev/2.5/v/missing",
            }
        ]
    }
    response = client.delete("/ipv4?cidr=192.168.3.1", headers=headers)
    assert response.status_code == 404
    assert response.json() == {
        "detail": "IP not found",
    }
    response = client.delete("/ipv4?cidr=192.168.3.1")
    assert response.status_code == 401
    assert response.json() == {
        "detail": "Invalid or missing API Key",
    }
