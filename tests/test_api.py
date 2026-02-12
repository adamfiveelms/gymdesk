from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_homepage_loads():
    response = client.get("/")
    assert response.status_code == 200
    assert "AdamDesk" in response.text


def test_navigation_pages_load():
    for path, label in [
        ("/members", "All Members"),
        ("/classes", "Class Schedule"),
        ("/leads", "Lead Pipeline"),
        ("/billing", "Billing & Invoices"),
        ("/reports", "Revenue Snapshot"),
    ]:
        response = client.get(path)
        assert response.status_code == 200
        assert label in response.text
