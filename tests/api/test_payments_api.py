import pytest
import requests

pytestmark = pytest.mark.api


def test_health(app_url):
    r = requests.get(f"{app_url}/health", timeout=5)
    assert r.status_code == 200 and r.json()["status"] == "ok"


@pytest.mark.smoke
def test_create_and_list_payment(app_url):
    r = requests.post(
        f"{app_url}/api/payments", json={"beneficiary": "Acme Ltd", "amount": 99.5, "currency": "EUR"}, timeout=5
    )
    assert r.status_code == 201
    body = r.json()
    assert body["status"] == "ACCEPTED" and body["id"].startswith("PAY-")
    ids = [p["id"] for p in requests.get(f"{app_url}/api/payments", timeout=5).json()]
    assert body["id"] in ids


@pytest.mark.parametrize(
    "payload",
    [
        {"beneficiary": "Acme", "amount": -1, "currency": "GBP"},
        {"beneficiary": "Acme", "amount": 10, "currency": "JPY"},
        {"beneficiary": "", "amount": 10, "currency": "GBP"},
    ],
)
def test_invalid_payment_rejected(app_url, payload):
    assert requests.post(f"{app_url}/api/payments", json=payload, timeout=5).status_code == 422
