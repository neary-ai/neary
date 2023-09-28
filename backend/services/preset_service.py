from sqlalchemy.orm import Session
from backend import models

def get_preset_by_name(db: Session, preset_name: str):
    return db.query(models.PresetModel).filter(models.PresetModel.name == preset_name).first()

def get_active_presets(db: Session):
    return db.query(models.PresetModel).filter(models.PresetModel.is_active == True).all()

def get_default_preset(db: Session):
    return db.query(models.PresetModel).filter(models.PresetModel.is_default == True).first()

def create_preset(db: Session, preset_data):
    preset = models.PresetModel(**preset_data)
    db.add(preset)
    db.commit()
    db.refresh(preset)
    return preset

def update_preset(db: Session, preset: models.PresetModel, preset_data):
    for key, value in preset_data.items():
        setattr(preset, key, value)
    db.commit()
    return preset