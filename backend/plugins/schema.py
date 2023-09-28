from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class Metadata(BaseModel):
    name: str
    display_name: str
    description: str
    icon: str
    version: str
    author: str
    url: str

class ItemProperty(BaseModel):
    type: str
    description: str
    required: bool

class Item(BaseModel):
    type: str
    properties: Optional[Dict[str, ItemProperty]] = None
    description: Optional[str] = None
    required: Optional[bool] = None

class Parameter(BaseModel):
    type: str
    description: str
    required: bool
    items: Optional[Item] = None

class Setting(BaseModel):
    description: str
    value: Optional[Any] = None
    type: str
    editable: bool

class Snippet(BaseModel):
    display_name: str
    description: str
    settings: Dict[str, Setting] = {}
    integrations: List[str] = []

class Tool(BaseModel):
    display_name: str
    description: str
    llm_description: str
    parameters: Dict[str, Parameter] = {}
    settings: Dict[str, Setting]
    integrations: List[str] = []

class PluginConfig(BaseModel):
    metadata: Metadata
    snippets: Dict[str, Snippet] = {}
    tools: Dict[str, Tool] = {}
