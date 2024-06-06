#
# Unit Test Code rest api
#
# pytest -v tests/test_cidr_api2.py
#
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import copy
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))
from cidr_api2 import app, get_db

HEADERS = {
    "x-api-key": "apitest",
    "Content-Type": "application/json",
}
def format_missing_test(rec):
    ### test for fastapi 0.90
    if 'url' in rec["detail"][0]:
        del rec["detail"][0]['url']

    return rec

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


def test_ipv4_post_country():
    json_data = {"cidr": "192.168.1.0/24", "country": "JP"}
    response = client.post("/ipv4/country", headers=HEADERS, json=json_data)
    assert response.status_code == 200
    assert response.json() == {
        "cidr": "192.168.1.0/24",
        "country": "JP",
    }


def test_ipv4_post_asn():
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


def test_ipv4_post_city():
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


def test_ipv4_post_all():
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


def test_ipv4_put_all():
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


def test_ipv4_search():
    response = client.get("/ipv4/search?ipv4=192.168.1.2")
    assert response.status_code == 200
    assert response.json() == {
        "cidr": "192.168.1.0/24",
        "country": "JP",
        "asn": 10000,
        "provider": "Mukogawa Net.",
        "city": "兵庫県尼崎市",
    }

    response = client.get("/ipv4/search?ipv4=192.168.3.2")
    assert response.status_code == 200
    assert response.json() == {
        "cidr": "192.168.3.0/24",
        "country": "JP",
        "asn": 10002,
        "provider": "Mukogawa3 Net.",
        "city": "兵庫県西宮市",
    }


def test_ipv4_delete():
    headers = {
        "x-api-key": "apitest",
    }

    response = client.delete("/ipv4?cidr=192.168.1.0/24", headers=headers)
    assert response.status_code == 200
    assert response.json() == "OK"

    response = client.delete("/ipv4?cidr=192.168.3.0/24", headers=headers)
    assert response.status_code == 200
    assert response.json() == "OK"


def test_ipv4_error_post_country():
    json_data = {"cidr": "192.168.1.0/24", "country": "JP"}
    assert_body = make_assert_data(json_data, client.post, "/ipv4/country")
    assert_body("ip_v4_network", cidr="2001:268:fa03:500:175:129:0:103")
    assert_body("string_too_short", country="J")
    assert_body("string_too_long", country="JP1")
    assert_body("string_type", country=10)


def test_ipv4_error_post_asn():
    json_data = {
        "cidr": "192.168.1.0/24",
        "asn": 10000,
        "provider": "Mukogawa Net.",
    }
    assert_body = make_assert_data(json_data, client.post, "/ipv4/asn")
    assert_body("ip_v4_network", cidr="2001:268:fa03:500:175:129:0:103")
    assert_body("int_parsing", asn="a")
    assert_body("string_type", provider=10)


def test_ipv4_error_post_city():
    json_data = {
        "cidr": "192.168.1.0/24",
        "city": "兵庫県尼崎市",
    }
    assert_body = make_assert_data(json_data, client.post, "/ipv4/city")
    assert_body("ip_v4_network", cidr="2001:268:fa03:500:175:129:0:103")
    assert_body("string_type", city=10)


def test_ipv4_error_post_all():
    json_data = {
        "cidr": "192.168.3.0/24",
        "country": "JP",
        "asn": 10002,
        "provider": "Mukogawa3 Net.",
        "city": "兵庫県芦屋市",
    }

    assert_body = make_assert_data(json_data, client.post, "/ipv4")
    assert_body("ip_v4_network", cidr="2001:268:fa03:500:175:129:0:103")
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

def test_ipv4_error_put_all():
    response = client.put("/ipv4?cidr=192.168.3.0/24", headers=HEADERS)
    assert response.status_code == 422
    assert format_missing_test(response.json()) == {
        "detail": [
            {
                "input": None,
                "loc": [
                    "body",
                ],
                "msg": "Field required",
                "type": "missing",
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
    assert_body = make_assert_data(json_data, client.put, "/ipv4?cidr=2001:268:fa03:500:175:129:0:103")
    assert_body("ip_v4_network")

    assert_body = make_assert_data(json_data, client.put, "/ipv4?cidr=192.168.3.0/24")
    assert_body("ip_v4_network", cidr="2001:268:fa03:500:175:129:0:103")
    assert_body("string_too_short", country="J")
    assert_body("string_too_long", country="JP1")
    assert_body("string_type", country=10)
    assert_body("int_parsing", asn="a")
    assert_body("string_type", provider=10)
    assert_body("string_type", city=10)


def test_ipv4_error_search():
    response = client.get("/ipv4/search?ipv4=2001:268:fa03:500:175:129:0:103")
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "type": "ip_v4_address",
                "loc": ["query", "ipv4"],
                "msg": "Input is not a valid IPv4 address",
                "input": "2001:268:fa03:500:175:129:0:103",
            }
        ]
    }
    response = client.get("/ipv4/search")
    assert response.status_code == 422
    assert format_missing_test(response.json()) == {
        "detail": [
            {
                "type": "missing",
                "loc": ["query", "ipv4"],
                "msg": "Field required",
                "input": None,
            }
        ]
    }
    response = client.get("/ipv4/search?ipv4=172.17.0.11")
    assert response.status_code == 404
    assert response.json() == {
        "detail": "IP not found",
    }


def test_ipv4_error_delete():
    headers = {
        "x-api-key": "apitest",
    }
    response = client.delete("/ipv4?cidr=2001:268:fa03:500:175:129:0:103", headers=headers)
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "type": "ip_v4_network",
                "loc": ["query", "cidr"],
                "msg": "Input is not a valid IPv4 network",
                "input": "2001:268:fa03:500:175:129:0:103",
            }
        ]
    }
    response = client.delete("/ipv4", headers=headers)
    assert response.status_code == 422
    assert format_missing_test(response.json()) == {
        "detail": [
            {
                "type": "missing",
                "loc": ["query", "cidr"],
                "msg": "Field required",
                "input": None,
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


def test_ipv6_post_country():
    json_data = {"cidr": "fda6:eacc:b448:1::/64", "country": "JP"}
    response = client.post("/ipv6/country", headers=HEADERS, json=json_data)
    assert response.status_code == 200
    assert response.json() == {
        "cidr": "fda6:eacc:b448:1::/64",
        "country": "JP",
    }


def test_ipv6_post_asn():
    json_data = {
        "cidr": "fda6:eacc:b448:1::/64",
        "asn": 10000,
        "provider": "Mukogawa Net.",
    }
    response = client.post("/ipv6/asn", headers=HEADERS, json=json_data)
    assert response.status_code == 200
    assert response.json() == {
        "cidr": "fda6:eacc:b448:1::/64",
        "asn": 10000,
        "provider": "Mukogawa Net.",
    }


def test_ipv6_post_city():
    json_data = {
        "cidr": "fda6:eacc:b448:1::/64",
        "city": "兵庫県尼崎市",
    }
    response = client.post("/ipv6/city", headers=HEADERS, json=json_data)
    assert response.status_code == 200
    assert response.json() == {
        "cidr": "fda6:eacc:b448:1::/64",
        "city": "兵庫県尼崎市",
    }


def test_ipv6_post_all():
    json_data = {
        "cidr": "fda6:eacc:b448:3::/64",
        "country": "JP",
        "asn": 10001,
        "provider": "Mukogawa2 Net.",
        "city": "兵庫県宝塚市",
    }
    response = client.post("/ipv6", headers=HEADERS, json=json_data)
    assert response.status_code == 200
    assert response.json() == {
        "cidr": "fda6:eacc:b448:3::/64",
        "country": "JP",
        "asn": 10001,
        "provider": "Mukogawa2 Net.",
        "city": "兵庫県宝塚市",
    }


def test_ipv6_put_all():
    json_data = {
        "cidr": "fda6:eacc:b448:3::/64",
        "country": "JP",
        "asn": 10002,
        "provider": "Mukogawa3 Net.",
        "city": "兵庫県西宮市",
    }
    response = client.put("/ipv6?cidr=fda6:eacc:b448:3::/64", headers=HEADERS, json=json_data)
    assert response.status_code == 200
    assert response.json() == {
        "cidr": "fda6:eacc:b448:3::/64",
        "country": "JP",
        "asn": 10002,
        "provider": "Mukogawa3 Net.",
        "city": "兵庫県西宮市",
    }


def test_ipv6_search():
    response = client.get("/ipv6/search?ipv6=fda6:eacc:b448:1:524:352e:ea4c:977d")
    assert response.status_code == 200
    assert response.json() == {
        "cidr": "fda6:eacc:b448:1::/64",
        "country": "JP",
        "asn": 10000,
        "provider": "Mukogawa Net.",
        "city": "兵庫県尼崎市",
    }

    response = client.get("/ipv6/search?ipv6=fda6:eacc:b448:3:524:352e:ea4c:977d")
    assert response.status_code == 200
    assert response.json() == {
        "cidr": "fda6:eacc:b448:3::/64",
        "country": "JP",
        "asn": 10002,
        "provider": "Mukogawa3 Net.",
        "city": "兵庫県西宮市",
    }


def test_ipv6_delete():
    headers = {
        "x-api-key": "apitest",
    }

    response = client.delete("/ipv6?cidr=fda6:eacc:b448:1::/64", headers=headers)
    assert response.status_code == 200
    assert response.json() == "OK"

    response = client.delete("/ipv6?cidr=fda6:eacc:b448:3::/64", headers=headers)
    assert response.status_code == 200
    assert response.json() == "OK"


def test_ipv6_error_post_country():
    json_data = {"cidr": "fda6:eacc:b448:1::/64", "country": "JP"}
    assert_body = make_assert_data(json_data, client.post, "/ipv6/country")
    assert_body("ip_v6_network", cidr="192.168.1.0/24")
    assert_body("string_too_short", country="J")
    assert_body("string_too_long", country="JP1")
    assert_body("string_type", country=10)


def test_ipv6_error_post_asn():
    json_data = {
        "cidr": "fda6:eacc:b448:1::/64",
        "asn": 10000,
        "provider": "Mukogawa Net.",
    }
    assert_body = make_assert_data(json_data, client.post, "/ipv6/asn")
    assert_body("ip_v6_network", cidr="192.168.1.0/24")
    assert_body("int_parsing", asn="a")
    assert_body("string_type", provider=10)


def test_ipv6_error_post_city():
    json_data = {
        "cidr": "fda6:eacc:b448:1::/64",
        "city": "兵庫県尼崎市",
    }
    assert_body = make_assert_data(json_data, client.post, "/ipv6/city")
    assert_body("ip_v6_network", cidr="192.168.1.0/24")
    assert_body("string_type", city=10)


def test_ipv6_error_post_all():
    json_data = {
        "cidr": "fda6:eacc:b448:3::/64",
        "country": "JP",
        "asn": 10002,
        "provider": "Mukogawa3 Net.",
        "city": "兵庫県芦屋市",
    }

    assert_body = make_assert_data(json_data, client.post, "/ipv6")
    assert_body("ip_v6_network", cidr="192.168.1.0/24")
    assert_body("string_too_short", country="J")
    assert_body("string_too_long", country="JP1")
    assert_body("string_type", country=10)
    assert_body("int_parsing", asn="a")
    assert_body("string_type", provider=10)
    assert_body("string_type", city=10)

    response = client.post("/ipv6", headers=HEADERS, json=json_data)
    assert response.status_code == 200

    response = client.post("/ipv6", headers=HEADERS, json=json_data)
    assert response.status_code == 422
    assert response.json() == { "detail": "Duplicate Error", }

    response = client.delete("/ipv6?cidr=fda6:eacc:b448:3::/64", headers={ "x-api-key": "apitest",})
    assert response.status_code == 200


def test_ipv6_error_put_all():
    response = client.put("/ipv6?cidr=fda6:eacc:b448:3::/64", headers=HEADERS)
    assert response.status_code == 422
    assert format_missing_test(response.json()) == {
        "detail": [
            {
                "input": None,
                "loc": [
                    "body",
                ],
                "msg": "Field required",
                "type": "missing",
            },
        ],
    }

    json_data = {
        "cidr": "fda6:eacc:b448:3::/64",
        "country": "JP",
        "asn": 10002,
        "provider": "Mukogawa3 Net.",
        "city": "兵庫県芦屋市",
    }
    assert_body = make_assert_data(json_data, client.put, "/ipv6?cidr=192.168.1.0/24")
    assert_body("ip_v6_network")

    assert_body = make_assert_data(json_data, client.put, "/ipv6?cidr=fda6:eacc:b448:3::/64")
    assert_body("ip_v6_network", cidr="192.168.1.0/24")
    assert_body("string_too_short", country="J")
    assert_body("string_too_long", country="JP1")
    assert_body("string_type", country=10)
    assert_body("int_parsing", asn="a")
    assert_body("string_type", provider=10)
    assert_body("string_type", city=10)


def test_ipv6_error_search():
    response = client.get("/ipv6/search?ipv6=192.168.1.1")
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "type": "ip_v6_address",
                "loc": ["query", "ipv6"],
                "msg": "Input is not a valid IPv6 address",
                "input": "192.168.1.1",
            }
        ]
    }
    response = client.get("/ipv6/search")
    assert response.status_code == 422
    assert format_missing_test(response.json()) == {
        "detail": [
            {
                "type": "missing",
                "loc": ["query", "ipv6"],
                "msg": "Field required",
                "input": None,
            }
        ]
    }
    response = client.get("/ipv6/search?ipv6=fda6:eacc:b448:2:524:352e:ea4c:977d")
    assert response.status_code == 404
    assert response.json() == {
        "detail": "IP not found",
    }


def test_ipv6_error_delete():
    headers = {
        "x-api-key": "apitest",
    }
    response = client.delete("/ipv6?cidr=192.168.1.0/24", headers=headers)
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "type": "ip_v6_network",
                "loc": ["query", "cidr"],
                "msg": "Input is not a valid IPv6 network",
                "input": "192.168.1.0/24",
            }
        ]
    }
    response = client.delete("/ipv6", headers=headers)
    assert response.status_code == 422
    assert format_missing_test(response.json()) == {
        "detail": [
            {
                "type": "missing",
                "loc": ["query", "cidr"],
                "msg": "Field required",
                "input": None,
            }
        ]
    }
    response = client.delete("/ipv6?cidr=fda6:eacc:b448:2:524:352e:ea4c:977d", headers=headers)
    assert response.status_code == 404
    assert response.json() == {
        "detail": "IP not found",
    }
    response = client.delete("/ipv6?cidr=fda6:eacc:b448:2:524:352e:ea4c:977d")
    assert response.status_code == 401
    assert response.json() == {
        "detail": "Invalid or missing API Key",
    }
