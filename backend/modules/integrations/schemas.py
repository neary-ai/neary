from typing import Optional, Any, List
from pydantic import BaseModel, ConfigDict


class IntegrationInstance(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    integration_id: int
    credentials: Optional[Any]


class Integration(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    display_name: str
    auth_method: str
    data: Optional[Any]

    instances: Optional[List[IntegrationInstance]] = []


class IntegrationCreate(BaseModel):
    id: int
    api_key: str
