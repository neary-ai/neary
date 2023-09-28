from sqlalchemy.orm import Session
from backend import models


def get_integration_by_name(db: Session, name: str):
    return db.query(models.IntegrationRegistryModel).filter(name=name).first()

def get_integrations(db: Session):
    return db.query(models.IntegrationRegistryModel).all()

def get_integration_instance(db: Session, integration: models.IntegrationRegistryModel):
    return db.query(models.IntegrationInstanceModel).filter(integration=integration).first()

def update_integration_credentials(db: Session, instance: models.IntegrationInstanceModel, credentials: dict):
    instance.credentials = credentials
    db.commit()