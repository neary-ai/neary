from typing import Optional, Any, List, ForwardRef
from pydantic import BaseModel, ConfigDict

IntegrationRef = ForwardRef("Integration")


class Function(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    type: str
    display_name: str
    description: Optional[str]
    llm_description: Optional[str]
    plugin_id: int
    settings_metadata: Optional[Any]
    parameters: Optional[Any]
    meta_data: Optional[Any]

    integrations: Optional[List[IntegrationRef]] = []


class FunctionInstance(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    function_id: int
    plugin_instance_id: int
    settings_values: Optional[Any]

    function: Function


class Plugin(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    display_name: str
    icon: Optional[str]
    description: Optional[str]
    author: Optional[str]
    url: Optional[str]
    version: Optional[str]
    settings_metadata: Optional[Any]
    is_enabled: bool

    functions: Optional[List[Function]] = []


class PluginInstance(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    plugin_id: int
    conversation_id: int
    settings_values: Optional[Any]
    data: Optional[Any]

    plugin: Plugin
    function_instances: Optional[List[FunctionInstance]] = []


from modules.integrations.schemas import Integration

Function.update_forward_refs()
