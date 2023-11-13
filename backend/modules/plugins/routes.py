from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session

from .models import *
from .schemas import *
from .services.plugin_service import PluginService
from database import get_db

router = APIRouter()


@router.get("/plugins", response_model=List[Plugin])
def get_plugins(db: Session = Depends(get_db)):
    return PluginService(db).get_plugins()


@router.get("/plugins/{plugin_id}", response_model=PluginInstance)
def get_plugin_instance(plugin_id: int, db: Session = Depends(get_db)):
    service = PluginService(db)
    plugin = service.get_plugin_instance_by_id(plugin_id)

    if plugin is None:
        raise HTTPException(status_code=404, detail="Plugin not found")

    return plugin


@router.get("/plugins/{plugin_id}/enable")
def enable_plugin(plugin_id: int, db: Session = Depends(get_db)):
    service = PluginService(db)

    plugin = service.get_plugin_by_id(id=plugin_id)

    if plugin:
        service.enable_plugin(plugin)
    else:
        raise HTTPException(status_code=404, detail="Plugin not found")

    return {"detail": f"Plugin enabled"}


@router.get("/plugins/{plugin_id}/disable")
def disable_plugin(plugin_id: int, db: Session = Depends(get_db)):
    service = PluginService(db)
    plugin = service.get_plugin_by_id(id=plugin_id)

    if plugin:
        service.disable_plugin(plugin)
    else:
        raise HTTPException(status_code=404, detail="Plugin not found")

    return {"detail": f"Plugin disabled"}


@router.put("/plugins/{plugin_id}/data")
async def clear_plugin_instance_data(plugin_id: int, db: Session = Depends(get_db)):
    service = PluginService(db)
    instance = service.get_plugin_instance_by_id(plugin_id)

    if instance:
        instance = service.clear_plugin_instance_data(instance)
    else:
        raise HTTPException(status_code=404, detail="Plugin instance not found")

    return {"detail": "Plugin data cleared"}


@router.put("/plugins/{plugin_id}")
async def update_plugin_instance(
    plugin_id: int, settings: dict = Body(...), db: Session = Depends(get_db)
):
    service = PluginService(db)

    try:
        result = service.update_plugin_instance(plugin_id, settings)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

    return result
