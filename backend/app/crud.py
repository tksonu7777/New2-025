from sqlalchemy.orm import Session
import secrets
from passlib.context import CryptContext
from . import models, schemas

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user_by_api_key(db: Session, api_key: str):
    return db.query(models.User).filter(models.User.api_key == api_key).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_all_icons(db: Session):
    return db.query(models.Icon).all()

def create_icon(db: Session, icon: schemas.IconCreate):
    db_icon = models.Icon(hash=icon.hash, app_name=icon.app_name)
    db.add(db_icon)
    db.commit()
    db.refresh(db_icon)
    return db_icon

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    api_key = secrets.token_urlsafe(32)
    db_user = models.User(
        username=user.username, hashed_password=hashed_password, api_key=api_key
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_screenshot(db: Session, screenshot: schemas.ScreenshotCreate):
    db_screenshot = models.Screenshot(hash=screenshot.hash, app_name=screenshot.app_name)
    db.add(db_screenshot)
    db.commit()
    db.refresh(db_screenshot)
    return db_screenshot

def get_screenshots(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Screenshot).offset(skip).limit(limit).all()
