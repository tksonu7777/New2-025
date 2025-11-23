from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class App(Base):
    __tablename__ = "apps"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    package_name = Column(String, unique=True, index=True)
    is_clone = Column(Boolean, default=False)
    is_fake = Column(Boolean, default=False)
    icon_hash = Column(String, nullable=True)
    permissions = relationship("Permission", back_populates="app")
    api_calls = relationship("ApiCall", back_populates="app")
    device_healths = relationship("DeviceHealth", back_populates="app")
    network_traffics = relationship("NetworkTraffic", back_populates="app")
    urls = relationship("Url", back_populates="app")

class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    is_hidden = Column(Boolean, default=False)
    app_id = Column(Integer, ForeignKey("apps.id"))

    app = relationship("App", back_populates="permissions")

class ApiCall(Base):
    __tablename__ = "api_calls"

    id = Column(Integer, primary_key=True, index=True)
    endpoint = Column(String, index=True)
    payload = Column(String)
    risk_score = Column(Integer)
    is_suspicious = Column(Boolean, default=False)
    app_id = Column(Integer, ForeignKey("apps.id"))

    app = relationship("App", back_populates="api_calls")

class DeviceHealth(Base):
    __tablename__ = "device_health"

    id = Column(Integer, primary_key=True, index=True)
    is_rooted = Column(Boolean, default=False)
    risk_score = Column(Integer)
    is_compromised = Column(Boolean, default=False)
    app_id = Column(Integer, ForeignKey("apps.id"))

    app = relationship("App", back_populates="device_healths")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    api_key = Column(String, unique=True, index=True)

class NetworkTraffic(Base):
    __tablename__ = "network_traffic"

    id = Column(Integer, primary_key=True, index=True)
    destination_ip = Column(String, index=True)
    risk_score = Column(Integer)
    is_suspicious = Column(Boolean, default=False)
    app_id = Column(Integer, ForeignKey("apps.id"))

    app = relationship("App", back_populates="network_traffics")

class Url(Base):
    __tablename__ = "urls"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, index=True)
    is_phishing = Column(Boolean, default=False)
    risk_score = Column(Integer)
    app_id = Column(Integer, ForeignKey("apps.id"))

    app = relationship("App", back_populates="urls")

class Icon(Base):
    __tablename__ = "icons"

    id = Column(Integer, primary_key=True, index=True)
    hash = Column(String, unique=True, index=True)
    app_name = Column(String)
