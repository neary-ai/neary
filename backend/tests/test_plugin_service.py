import pytest
from backend.schemas.preset import *
from backend.services.preset_service import PresetService
from backend.services.conversation_service import ConversationService
from backend.services.plugin_service import PluginService
from backend.services.plugin_manager import PluginManager


def test_load_plugin(db_session):
    plugin_manager = PluginManager(db_session)
    plugin_manager.load_plugin("essentials")

    plugin_data = plugin_manager.get_plugin("essentials")

    assert plugin_data["class"]
    assert plugin_data["metadata"]["name"] == "essentials"


def test_disable_plugin(db_session, client):
    plugin_manager = PluginManager(db_session)
    plugin_data = plugin_manager.get_plugin("essentials")
    plugin_id = plugin_data["metadata"]["id"]

    response = client.get(f"/api/{plugin_id}/disable")

    assert response.status_code == 200

    service = PluginService(db_session)
    plugin = service.get_plugin_by_id(plugin_id)

    assert plugin.is_enabled == False


def test_enable_plugin(db_session, client):
    plugin_manager = PluginManager(db_session)
    plugin_data = plugin_manager.get_plugin("essentials")
    plugin_id = plugin_data["metadata"]["id"]

    response = client.get(f"/api/{plugin_id}/enable")

    assert response.status_code == 200

    service = PluginService(db_session)
    plugin = service.get_plugin_by_id(plugin_id)

    assert plugin.is_enabled == True
