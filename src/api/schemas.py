from pydantic import BaseModel, ConfigDict
from typing import Optional


class ModelTypeModel(BaseModel):
    id: int
    model_name: str
    description: str
    default_hyperparameters: dict
    default_model_architecture: dict
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


class ModelEnqueueRequest(BaseModel):
    ticker: str
    model_id: int
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


class AssetModel(BaseModel):
    id: int
    ticker: str
    name: str
    sector: Optional[str]
    asset_type: str
    model_config = ConfigDict(from_attributes=True)


class UserResponse(BaseModel):
    id: int
    email: str


class UserCreate(BaseModel):
    username: str
    email: str
    password: str

