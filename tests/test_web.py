import pytest

from crs.web import create_app


@pytest.fixture()
def client():
    return create_app().test_client()


def ielts(v):
    return {"test": "ielts", "scores": {a: v for a in ("speaking", "listening", "reading", "writing")}}


BODY = {"marital_status": "single", "age": 29, "education": "bachelor", "first_language": ielts(7.0),
        "canadian_work_years": 1}


def test_index_renders(client):
    r = client.get("/")
    assert r.status_code == 200 and b"CRS" in r.data


def test_calculate_single(client):
    r = client.post("/api/calculate", json=BODY)
    assert r.status_code == 200
    d = r.get_json()
    # IELTS 7.0 speaking/reading/writing -> CLB 9; listening 7.0 -> CLB 7 (needs 8.0 for 9)
    assert d["sections"]["core"]["items"]["first_language"] == 31 * 3 + 17
    assert d["scored_as_couple"] is False and d["max"] == 1200


def test_spouse_accompanying_scored_as_couple(client):
    body = {**BODY, "marital_status": "married", "spouse_accompanying": True,
            "spouse": {"education": "master", "canadian_work_years": 2, "language": None}}
    d = client.post("/api/calculate", json=body).get_json()
    assert d["scored_as_couple"] and d["sections"]["spouse"]["total"] == 10 + 7


@pytest.mark.parametrize("extra", [{"spouse_accompanying": False}, {"spouse_is_citizen_or_pr": True,
                                                                     "spouse_accompanying": True}])
def test_married_but_not_counted_is_single(client, extra):
    body = {**BODY, "marital_status": "married", "spouse": {"education": "master"}, **extra}
    d = client.post("/api/calculate", json=body).get_json()
    assert not d["scored_as_couple"] and d["sections"]["spouse"]["total"] == 0


@pytest.mark.parametrize("patch", [{"age": 5}, {"education": "x"}, {"first_language": None},
                                   {"marital_status": "??"}, {"first_language": ielts(9.5)},
                                   {"second_language": ielts(7.0)}])
def test_bad_requests(client, patch):
    r = client.post("/api/calculate", json={**BODY, **patch})
    assert r.status_code == 400 and "error" in r.get_json()


def test_non_json_body(client):
    assert client.post("/api/calculate", data="nope").status_code == 400
