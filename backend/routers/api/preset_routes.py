from fastapi import HTTPException, APIRouter, Body

from backend.models import *

router = APIRouter()

@router.get("/")
async def get_presets():
    presets = await PresetModel.filter(is_active=True)
    presets = [preset.serialize() for preset in presets]
    return presets


@router.post("/")
async def create_preset(preset_data: dict = Body(...)):
    conversation = await ConversationModel.get_or_none(id=preset_data['conversation_id'])
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    conversation_plugins = await conversation.plugins.all()
    serialized_plugins = [await plugin.serialize() for plugin in conversation_plugins]

    plugins = []

    for plugin in serialized_plugins:
        plugins.append({
            "name": plugin['name'],
            "functions": plugin['functions'],
            "data": None
        })

    preset = await PresetModel.create(
        name=preset_data['name'],
        description=preset_data['description'],
        icon=preset_data['icon'],
        plugins=plugins,
        settings=conversation.settings,
        is_custom=True,
        is_active=True,
        is_default=False
    )

    serialized = preset.serialize()

    return serialized


@router.put("/{preset_id}")
async def update_preset(preset_id: int, preset_data: dict = Body(...)):
    preset_data = preset_data['preset']

    preset = await PresetModel.get_or_none(id=preset_id)
    if preset is None:
        raise HTTPException(status_code=404, detail="Preset not found")

    if 'rebuild_from_conversation' in preset_data:
        # Update preset with data from conversation
        conversation = await ConversationModel.get(id=preset_data['rebuild_from_conversation'])

        conversation_plugins = await conversation.plugins.all()
        serialized_plugins = [await plugin.serialize() for plugin in conversation_plugins]

        plugins = []

        for plugin in serialized_plugins:
            plugins.append({
                "name": plugin['name'],
                "functions": plugin['functions'],
                "data": None
            })

        preset.plugins = plugins
        preset.settings = conversation.settings
        preset.is_custom = True,
        await preset.save()

        print('Updated preset: ', preset.serialize())
    else:
        # If the updated preset is set to default, unset all other presets
        if preset_data['is_default']:
            await PresetModel.filter(is_default=True).update(is_default=False)

        preset.update_from_dict(preset_data)
        await preset.save()

    presets = await PresetModel.filter(is_active=True)
    presets = [preset.serialize() for preset in presets]
    return presets


@router.post("/{preset_id}")
async def delete_presets(preset_id: int):
    preset = await PresetModel.get_or_none(id=preset_id)

    if preset:
        # If the preset being deactivated is the default, set the first active preset as default
        if preset.is_default:
            first_active_preset = await PresetModel.filter(is_active=True).exclude(id=preset_id).first()
            if first_active_preset:
                first_active_preset.is_default = True
                await first_active_preset.save()

        preset.is_active = False
        preset.is_default = False
        await preset.save()

    presets = await PresetModel.filter(is_active=True)
    presets = [preset.serialize() for preset in presets]
    return presets


@router.get("/{preset_id}/export")
async def export_preset(preset_id: int):
    preset = await PresetModel.get_or_none(id=preset_id)
    if preset is None:
        raise HTTPException(status_code=404, detail="Preset not found")

    preset_data = preset.serialize()

    del preset_data['is_custom']
    del preset_data['is_default']
    del preset_data['id']

    return preset_data


@router.post("/import")
async def add_presets(preset: dict = Body(...)):
    existing_preset = await PresetModel.get_or_none(name=preset['name'], is_active=False)

    if existing_preset:
        await existing_preset.delete()

    await PresetModel.create(**preset, is_custom=True)

    presets = await PresetModel.filter(is_active=True)

    return [preset.serialize() for preset in presets]
