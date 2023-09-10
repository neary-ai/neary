from fastapi import HTTPException, APIRouter, Body

from backend.models import *
from backend.services import PluginManager

router = APIRouter()
plugin_manager = PluginManager()


@router.get("")
async def get_loaded_plugins():
    plugins = plugin_manager.get_serialized_plugins()
    return plugins


@router.get("/{plugin_id}")
async def get_plugin_instance(plugin_id: int):
    plugin = await PluginInstanceModel.get_or_none(id=plugin_id)
    if plugin:
        plugin_data = await plugin.serialize()

    return plugin_data


@router.get("/{plugin_id}/enable")
async def enable_plugin(plugin_id: int):
    plugin = await PluginRegistryModel.get_or_none(id=plugin_id)
    if plugin:
        plugin.is_enabled = True
        await plugin.save()


@router.get("/{plugin_id}/disable")
async def disable_plugin(plugin_id: int):
    plugin = await PluginRegistryModel.get_or_none(id=plugin_id)
    if plugin:
        plugin.is_enabled = False
        await plugin.save()


@router.put("/{plugin_name}/{conversation_id}")
async def update_plugin_instance(plugin_name: str, conversation_id: int, settings: dict = Body(...)):
    plugin = await PluginInstanceModel.get_or_none(name=plugin_name, conversation_id=conversation_id)

    if plugin is None:
        raise HTTPException(status_code=404, detail="Plugin not found")

    for function_type in ['snippets', 'tools']:
        for function_name, function_settings in settings.items():
            if function_type in plugin.functions and function_name in plugin.functions[function_type]:
                # Wrap each setting value in an object with a 'value' property
                function_settings = {key: {"value": value}
                                     for key, value in function_settings.items()}

                if 'settings' in plugin.functions[function_type][function_name]:
                    if plugin.functions[function_type][function_name]['settings'] is None:
                        # If the current settings are None, replace them with the new settings
                        plugin.functions[function_type][function_name]['settings'] = function_settings
                    else:
                        # If the current settings are not None, update them with the new settings
                        plugin.functions[function_type][function_name]['settings'].update(
                            function_settings)
                else:
                    # If the 'settings' field does not exist, create it and set it to the new settings
                    plugin.functions[function_type][function_name]['settings'] = function_settings

    await plugin.save()

    return {"detail": "success"}


@router.put("/{plugin_name}/{conversation_id}/data")
async def clear_plugin_data(plugin_name: str, conversation_id: int):
    plugin = await PluginInstanceModel.get_or_none(name=plugin_name, conversation_id=conversation_id)

    if plugin is None:
        raise HTTPException(status_code=404, detail="Plugin not found")

    plugin.data = {}

    await plugin.save()

    return {"detail": "success"}
