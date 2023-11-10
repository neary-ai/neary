import pytest
from backend.modules.conversations.conversation_service import ConversationService


def test_create_conversation_endpoint(client, db_session):
    # Prepare data for the request
    conversation_data = {
        "title": "Test Conversation",
        "preset_id": 1,
        "settings": {},
    }

    # Call the API endpoint to create a conversation
    response = client.post("/api/conversations", json=conversation_data)

    # Check the response status code and data
    assert response.status_code == 200
    data = response.json()

    # Check the data in the response
    assert data["title"] == "Test Conversation"
    assert data["preset_id"] == 1
    assert data["settings"] == {}
    assert "id" in data
