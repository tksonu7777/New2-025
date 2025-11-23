from fastapi.testclient import TestClient

def test_read_main(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}

def test_create_app(client, test_user):
    response = client.post(
        "/apps/",
        json={"name": "Test App clone", "package_name": "com.test.app"},
        headers={"X-API-KEY": test_user["api_key"]},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Test App clone"
    assert response.json()["package_name"] == "com.test.app"
    assert response.json()["is_clone"] == True
    assert response.json()["is_fake"] == False
    assert "id" in response.json()

def test_create_device_health_for_app(client, test_user):
    app_response = client.post(
        "/apps/",
        json={"name": "Test App", "package_name": "com.test.app"},
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
        json={"name": "Test App", "package_name": "com.test.app"},
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
