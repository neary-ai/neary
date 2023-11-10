import pytest
from backend.services.space_service import SpaceService


def test_create_space(db_session):
    # Create a space, and check if it's correctly created
    space_service = SpaceService(db_session)
    new_space = space_service.create_space(name="Test Space")
    assert new_space is not None
    assert new_space.name == "Test Space"


def test_create_space_endpoint(client):
    # Call the API endpoint to create a space
    response = client.post("/api/spaces", json={"name": "Test Space"})
    assert response.status_code == 200
    data = response.json()

    # Check the data in the response
    assert data["name"] == "Test Space"
    assert "id" in data


def test_update_space(db_session):
    # Create a space
    space_service = SpaceService(db_session)
    new_space = space_service.create_space(name="Test Space")

    # Update the space and check if it's correctly updated
    updated_space = space_service.update_space_name(new_space, "Updated Space")
    assert updated_space is not None
    assert updated_space.name == "Updated Space"


def test_update_space_endpoint(client, db_session):
    # Create a space
    space_service = SpaceService(db_session)
    new_space = space_service.create_space(name="Test Space")

    # Call the API endpoint to update the space
    response = client.put(f"/api/spaces/{new_space.id}", json={"name": "Updated Space"})
    assert response.status_code == 200
    data = response.json()

    # Check the data in the response
    assert data["name"] == "Updated Space"


def test_archive_space(db_session):
    # Create a space
    space_service = SpaceService(db_session)
    new_space = space_service.create_space(name="Test Space")

    # Archive the space and check if it's correctly archived
    archived_space = space_service.archive_space(new_space)
    assert archived_space is not None
    assert archived_space.is_archived == True


def test_archive_space_endpoint(client, db_session):
    # Create a space
    space_service = SpaceService(db_session)
    new_space = space_service.create_space(name="Test Space")

    # Call the API endpoint to archive the space
    response = client.put(f"/api/spaces/{new_space.id}/archive")
    assert response.status_code == 200
    data = response.json()

    # Check the data in the response
    assert data["is_archived"] == True
