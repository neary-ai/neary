from fastapi import HTTPException, APIRouter, Body

from backend.models import *
from backend.services import PluginManager

router = APIRouter()

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


@router.put("/{plugin_id}")
async def update_plugin_instance(plugin_id: int, settings: dict = Body(...)):
    plugin = await PluginInstanceModel.get_or_none(id=plugin_id)

    if plugin is None:
        raise HTTPException(status_code=404, detail="Plugin not found")

    await plugin.fetch_related('function_instances')
    
    for function_name, function_settings in settings.items():
        # Find the function in the plugin's functions array
        function = next((f for f in plugin.function_instances if f.name == function_name), None)

        if function:
            if function.settings_values is None:
                # If the current settings are None, replace them with the new settings
                function.settings_values = function_settings
            else:
                # If the current settings are not None, update them with the new settings
                function.settings_values.update(function_settings)
                
            await function.save()

    await plugin.save()

    return {"detail": "success"}

@router.put("/{plugin_id}/data")
async def clear_plugin_data(plugin_id: int):
    plugin = await PluginInstanceModel.get_or_none(id=plugin_id)

    if plugin is None:
        raise HTTPException(status_code=404, detail="Plugin not found")

    plugin.data = {}

    await plugin.save()

    return {"detail": "success"}
