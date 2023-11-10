import pytest
from backend.schemas.preset import *
from backend.services.preset_service import PresetService
from backend.services.conversation_service import ConversationService


def test_create_preset(db_session):
    # Create a preset, and check if it's correctly created
    preset_service = PresetService(db_session)
    new_preset = preset_service.create_preset(
        name="Test Preset",
        description="Test description",
        icon="test_icon.png",
        plugins=[],
        settings={},
        is_default=False,
        is_custom=True,
    )
    assert new_preset is not None
    assert new_preset.name == "Test Preset"
    assert new_preset.is_custom == True


def test_create_preset_endpoint(client):
    # Call the API endpoint to create a preset
    response = client.post(
        "/api/presets/import",
        json={
            "name": "Test Preset 2",
            "description": "Test description",
            "icon": "test_icon.png",
            "plugins": [],
            "settings": {},
            "is_default": False,
            "is_custom": True,
        },
    )
    print(response.content)
    assert response.status_code == 200
    data = response.json()

    # Check the data in the response
    assert data["name"] == "Test Preset 2"
    assert "id" in data
    assert data["is_custom"] == True


def test_create_preset_from_conversation(db_session):
    # Create preset
    preset_service = PresetService(db_session)
    new_preset = preset_service.create_preset(
        name="Test Preset 5",
        description="Test description",
        icon="test_icon.png",
        plugins=[],
        settings={},
        is_default=False,
        is_custom=True,
    )

    # Create conversation with preset
    conversation_service = ConversationService(db_session)
    conversation = conversation_service.create_conversation(
        title="Test Conversation", preset_id=new_preset.id, settings=new_preset.settings
    )

    # Create a preset from the conversation
    preset = preset_service.create_preset_from_conversation(
        conversation.id, name="Custom Preset Name", icon="custom_icon.png"
    )

    assert preset is not None
    assert preset.name == "Custom Preset Name"
    assert preset.icon == "custom_icon.png"
    assert preset.plugins == conversation.plugins
    assert preset.settings == conversation.settings


def test_create_preset_from_conversation_endpoint(client):
    # Create a conversation
    conversation_data = {
        "title": "Test Conversation",
        "preset_id": 1,
        "settings": {},
    }
    response = client.post("/api/conversations", json=conversation_data)
    conversation_id = response.json()["id"]

    # Call the API endpoint to create a preset from the conversation
    response = client.post(
        f"/api/presets/from_conversation/{conversation_id}",
        json={
            "name": "Custom Preset Name 2",
            "icon": "custom_icon.png",
            "description": "Some cool preset",
        },
    )

    assert response.status_code == 200
    data = response.json()

    # Check the data in the response
    assert "id" in data
    assert data["name"] == "Custom Preset Name 2"
    assert data["description"] == "Some cool preset"
    assert data["icon"] == "custom_icon.png"


def test_update_preset(db_session):
    # Create a preset
    preset_service = PresetService(db_session)
    preset = preset_service.create_preset(
        name="Test Preset 3",
        description="Test description",
        icon="test_icon.png",
        plugins=[],
        settings={},
        is_default=False,
        is_custom=True,
    )

    # Update the preset
    updated_preset = preset_service.update_preset(
        preset.id, PresetUpdate(name="Updated Preset")
    )

    assert updated_preset is not None
    assert updated_preset.name == "Updated Preset"


def test_update_preset_endpoint(client):
    # Create a preset
    response = client.post(
        "/api/presets/import",
        json={
            "name": "Test Preset 4",
            "description": "Test description",
            "icon": "test_icon.png",
            "plugins": [],
            "settings": {},
            "is_default": False,
            "is_custom": True,
        },
    )
    preset_id = response.json()["id"]

    # Call the API endpoint to update the preset
    response = client.put(
        f"/api/presets/{preset_id}", json={"name": "Updated Preset 2"}
    )
    assert response.status_code == 200
    data = response.json()

    # Check the data in the response
    assert data["name"] == "Updated Preset 2"


def test_update_preset_from_conversation(db_session):
    # Create a conversation and a preset
    conversation_service = ConversationService(db_session)
    conversation = conversation_service.create_conversation(
        title="Test Conversation", preset_id=1, settings={"approval_required": False}
    )

    preset_service = PresetService(db_session)
    preset = preset_service.create_preset(
        name="Test Preset 6",
        description="Test description",
        icon="test_icon.png",
        plugins=[],
        settings={"approval_required": True},
        is_default=False,
        is_custom=True,
    )

    # Update the preset from the conversation
    updated_preset = preset_service.update_preset_from_conversation(
        preset.id, conversation.id
    )

    assert updated_preset is not None
    assert updated_preset.settings == {"approval_required": False}


def test_update_preset_from_conversation_endpoint(client):
    # Create a conversation and a preset
    conversation_data = {
        "title": "Test Conversation",
        "preset_id": 1,
        "settings": {"approval_required": False},
    }
    response = client.post("/api/conversations", json=conversation_data)
    conversation_id = response.json()["id"]

    response = client.post(
        "/api/presets/import",
        json={
            "name": "Test Preset 7",
            "description": "Test description",
            "icon": "test_icon.png",
            "plugins": [],
            "settings": {"approval_required": True},
            "is_default": False,
            "is_custom": True,
        },
    )
    print(response.content)
    preset_id = response.json()["id"]

    # Call the API endpoint to update the preset from the conversation
    response = client.put(
        f"/api/presets/{preset_id}/from_conversation/{conversation_id}"
    )
    assert response.status_code == 200
    data = response.json()

    # Check the data in the response
    assert data["settings"] == {"approval_required": False}


def test_get_all_presets(db_session):
    # Create some presets
    preset_service = PresetService(db_session)
    preset_service.create_preset(
        name="Test Preset 9",
        description="Test description",
        icon="test_icon.png",
        plugins=[],
        settings={},
        is_default=False,
        is_custom=True,
    )
    preset_service.create_preset(
        name="Test Preset 10",
        description="Test description",
        icon="test_icon.png",
        plugins=[],
        settings={},
        is_default=False,
        is_custom=True,
    )

    # Get all presets
    all_presets = preset_service.get_presets()

    assert len(all_presets) > 1
    assert all_presets[-1].name == "Test Preset 10"


def test_get_all_presets_endpoint(client):
    # Call the API endpoint to get all presets
    response = client.get("/api/presets")
    assert response.status_code == 200
    data = response.json()

    # Check the data in the response
    assert len(data) > 1
    assert data[-1]["name"] == "Test Preset 10"


def test_export_preset_endpoint(client):
    # Create a preset
    response = client.post(
        "/api/presets/import",
        json={
            "name": "Test Preset 11",
            "description": "Test description",
            "icon": "test_icon.png",
            "plugins": [],
            "settings": {},
            "is_default": False,
            "is_custom": True,
        },
    )
    preset_id = response.json()["id"]

    # Call the API endpoint to export the preset
    response = client.get(f"/api/presets/{preset_id}/export")
    assert response.status_code == 200
    data = response.json()

    # Check the data in the response
    assert data["name"] == "Test Preset 11"
    assert "id" not in data
    assert "is_default" not in data


def test_delete_preset(db_session):
    # Create a default preset and a second preset
    preset_service = PresetService(db_session)
    preset1 = preset_service.create_preset(
        name="Test Preset 12",
        description="Test description",
        icon="test_icon.png",
        plugins=[],
        settings={},
        is_default=True,
        is_custom=True,
    )
    preset2 = preset_service.create_preset(
        name="Test Preset 13",
        description="Test description",
        icon="test_icon.png",
        plugins=[],
        settings={},
        is_default=False,
        is_custom=True,
    )

    # Delete the default preset
    preset_service.delete_preset(preset1.id)

    # Check that new preset is default
    presets = preset_service.get_presets()
    assert presets[0].is_default == True
    assert presets[0].name != "Test Preset 12"


def test_delete_preset_endpoint(client):
    # Create a default preset and a second preset
    response = client.post(
        "/api/presets/import",
        json={
            "name": "Test Preset 14",
            "description": "Test description",
            "icon": "test_icon.png",
            "plugins": [],
            "settings": {},
            "is_default": True,
            "is_custom": True,
        },
    )
    preset1_id = response.json()["id"]

    response = client.post(
        "/api/presets/import",
        json={
            "name": "Test Preset 15",
            "description": "Test description",
            "icon": "test_icon.png",
            "plugins": [],
            "settings": {},
            "is_default": False,
            "is_custom": True,
        },
    )
    preset2_id = response.json()["id"]

    # Call the API endpoint to delete the default preset
    response = client.delete(f"/api/presets/{preset1_id}")
    assert response.status_code == 200

    # Check that the second preset is now the default
    response = client.get(f"/api/presets")
    assert response.status_code == 200
    data = response.json()
    assert data[0]["is_default"] == True
    assert data[0]["name"] != "Test Preset 14"
