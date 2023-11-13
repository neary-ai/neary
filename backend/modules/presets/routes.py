from typing import List

from sqlalchemy.orm import Session
from fastapi import HTTPException, APIRouter, Depends

from backend.database import get_db
from .schemas import *
from .services.preset_service import PresetService

router = APIRouter()


@router.post("/import", response_model=Preset)
def import_preset(preset: PresetCreate, db: Session = Depends(get_db)):
    service = PresetService(db)
    db_preset = service.create_preset(
        name=preset.name,
        description=preset.description,
        icon=preset.icon,
        plugins=preset.plugins,
        settings=preset.settings,
        is_default=preset.is_default,
        is_custom=preset.is_custom,
    )

    if db_preset is None:
        raise HTTPException(status_code=400, detail="Preset could not be created")

    return db_preset


@router.post("/from_conversation/{conversation_id}", response_model=Preset)
def create_preset_from_conversation(
    conversation_id: int, preset: PresetFromConversation, db: Session = Depends(get_db)
):
    service = PresetService(db)
    db_preset = service.create_preset_from_conversation(
        conversation_id,
        name=preset.name,
        description=preset.description,
        icon=preset.icon,
    )

    if db_preset is None:
        raise HTTPException(status_code=400, detail="Preset could not be created")

    return db_preset


@router.get("", response_model=List[Preset])
def get_presets(db: Session = Depends(get_db)):
    service = PresetService(db)
    presets = service.get_presets()

    if not presets:
        raise HTTPException(status_code=404, detail="No presets found")

    return presets


@router.put("/{preset_id}/from_conversation/{conversation_id}", response_model=Preset)
def update_preset_from_conversation(
    preset_id: int, conversation_id: int, db: Session = Depends(get_db)
):
    service = PresetService(db)
    db_preset = service.update_preset_from_conversation(preset_id, conversation_id)

    if db_preset is None:
        raise HTTPException(status_code=400, detail="Preset could not be updated")

    return db_preset


@router.put("/{preset_id}", response_model=Preset)
def update_preset(preset_id: int, preset: PresetUpdate, db: Session = Depends(get_db)):
    service = PresetService(db)
    db_preset = service.update_preset(preset_id, preset)

    if db_preset is None:
        raise HTTPException(status_code=404, detail="Preset not found")

    return db_preset


@router.delete("/{preset_id}")
def delete_preset(preset_id: int, db: Session = Depends(get_db)):
    service = PresetService(db)
    service.delete_preset(preset_id)

    return {"detail": f"Preset {preset_id} deleted"}


@router.get("/{preset_id}/export", response_model=PresetExport)
def export_preset(preset_id: int, db: Session = Depends(get_db)):
    service = PresetService(db)
    db_preset = service.get_preset_by_id(preset_id)

    if db_preset is None:
        raise HTTPException(status_code=404, detail="Preset not found")

    return db_preset
