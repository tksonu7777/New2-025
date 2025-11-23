from fastapi.testclient import TestClient
from app import threat_intelligence

def test_read_main(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}

def test_create_app_clone(client, test_user):
    response = client.post(
        "/apps/",
        json={"name": "Test App clone", "package_name": "com.test.app.clone", "icon_b64": ""},
        headers={"X-API-KEY": test_user["api_key"]},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Test App clone"
    assert response.json()["package_name"] == "com.test.app.clone"
    assert response.json()["is_clone"] == True
    assert response.json()["is_fake"] == False
    assert "id" in response.json()

def test_create_app_fake(client, test_user):
    response = client.post(
        "/apps/",
        json={"name": "Test App fake", "package_name": "com.test.app.fake", "icon_b64": ""},
        headers={"X-API-KEY": test_user["api_key"]},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Test App fake"
    assert response.json()["package_name"] == "com.test.app.fake"
    assert response.json()["is_clone"] == False
    assert response.json()["is_fake"] == True
    assert "id" in response.json()

def test_create_device_health_for_app(client, test_user):
    app_response = client.post(
        "/apps/",
        json={"name": "Test App", "package_name": "com.test.app", "icon_b64": ""},
        headers={"X-API-KEY": test_user["api_key"]},
    )
    app_id = app_response.json()["id"]
    response = client.post(
        f"/apps/{app_id}/device_health/",
        json={"is_rooted": True},
        headers={"X-API-KEY": test_user["api_key"]},
    )
    assert response.status_code == 200
    assert response.json()["is_rooted"] == True
    assert response.json()["is_compromised"] == True
    assert "id" in response.json()

def test_create_network_traffic_for_app(client, test_user):
    app_response = client.post(
        "/apps/",
        json={"name": "Test App", "package_name": "com.test.app", "icon_b64": ""},
        headers={"X-API-KEY": test_user["api_key"]},
    )
    app_id = app_response.json()["id"]
    response = client.post(
        f"/apps/{app_id}/network_traffic/",
        json={"destination_ip": "8.8.8.8"},
        headers={"X-API-KEY": test_user["api_key"]},
    )
    assert response.status_code == 200
    assert response.json()["destination_ip"] == "8.8.8.8"
    assert "id" in response.json()

def test_create_url_for_app(client, test_user, monkeypatch):
    def mock_check_url_virustotal(url):
        return {"harmless": 0, "malicious": 1, "suspicious": 0}

    monkeypatch.setattr(threat_intelligence, "check_url_virustotal", mock_check_url_virustotal)

    app_response = client.post(
        "/apps/",
        json={"name": "Test App", "package_name": "com.test.app", "icon_b64": ""},
        headers={"X-API-KEY": test_user["api_key"]},
    )
    app_id = app_response.json()["id"]
    response = client.post(
        f"/apps/{app_id}/urls/",
        json={"url": "https://example-login.com"},
        headers={"X-API-KEY": test_user["api_key"]},
    )
    assert response.status_code == 200
    assert response.json()["url"] == "https://example-login.com"
    assert response.json()["is_phishing"] == True
    assert response.json()["risk_score"] == 9
    assert "id" in response.json()
