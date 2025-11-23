from pydantic import BaseModel
from typing import List

class PermissionBase(BaseModel):
    name: str
    is_hidden: bool

class PermissionCreate(PermissionBase):
    pass

class Permission(PermissionBase):
    id: int
    app_id: int

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    api_key: str

    class Config:
        orm_mode = True

class DeviceHealthBase(BaseModel):
    is_rooted: bool

class DeviceHealthCreate(DeviceHealthBase):
    pass

class DeviceHealth(DeviceHealthBase):
    id: int
    risk_score: int
    is_compromised: bool
    app_id: int

    class Config:
        orm_mode = True

class NetworkTrafficBase(BaseModel):
    destination_ip: str

class NetworkTrafficCreate(NetworkTrafficBase):
    pass

class NetworkTraffic(NetworkTrafficBase):
    id: int
    risk_score: int
    is_suspicious: bool
    app_id: int

    class Config:
        orm_mode = True

class ApiCallBase(BaseModel):
    endpoint: str
    payload: str

class ApiCallCreate(ApiCallBase):
    pass

class ApiCall(ApiCallBase):
    id: int
    app_id: int
    risk_score: int
    is_suspicious: bool

    class Config:
        orm_mode = True

class AppBase(BaseModel):
    name: str
    package_name: str

class AppCreate(AppBase):
    pass

class App(AppBase):
    id: int
    is_clone: bool
    is_fake: bool
    permissions: List[Permission] = []
    api_calls: List[ApiCall] = []

    class Config:
        orm_mode = True
