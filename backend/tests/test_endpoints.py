import pytest

def test_initialize(client):
    response = client.get("/api/initialize")
    assert response.status_code == 200
    data = response.json()

    # Check that data is a dictionary
    assert isinstance(data, dict)

    # Check that all keys exist in the returned data
    expected_keys = ['app_state', 'user_profile', 'spaces', 'conversations', 'plugins', 'presets', 'integrations']
    assert all(key in data for key in expected_keys)

def test_create_conversation(client):
    # Replace with the actual values you expect to send and receive
    test_request_payload = {"space_id": -1}

    response = client.post("/api/conversations", json=test_request_payload)

    data = response.json()

    # Check that data is a dictionary
    assert isinstance(data, dict)

    # Check that all keys exist in the returned data
    expected_keys = ['id', 'preset', 'title', 'settings', 'plugins', 'messages', 'created_at']
    assert all(key in data for key in expected_keys)

def test_create_space(client):
    test_request_payload = {"name": "Test Space"}

    response = client.post("/api/spaces", json=test_request_payload)

    data = response.json()

    assert data['id'] > 0
    assert data['name'] == "Test Space"

def test_update_space(client):
    # Replace with the actual values you expect to send and receive
    test_request_payload = {"name": "Updated Space"}

    response = client.put("/api/spaces/1", json=test_request_payload)

    data = response.json()
    print(data)
    assert data['id'] > 0
    assert data['name'] == "Updated Space"

def test_archive_space(client):
    # Replace with the actual values you expect to send and receive
    test_request_payload = {}

    response = client.patch("/api/spaces/1", json=test_request_payload)

    data = response.json()
    print(data)
    assert data['id'] > 0
    assert data['is_archived'] == True