from typing import List
from fastapi import Depends, FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from . import schemas
from sqlalchemy.orm import Session
from . import models, schemas, security, crud
from .database import SessionLocal, engine, Base, get_db
from .websockets import manager
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from PIL import Image
import io
import base64
from imagehash import average_hash

def create_tables():
    Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_tables()

api_key_header = APIKeyHeader(name="X-API-KEY")

async def get_current_user(api_key: str = Depends(api_key_header), db: Session = Depends(get_db)):
    user = crud.get_user_by_api_key(db, api_key)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return user

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db=db, user=user)

@app.post("/token")
async def login_for_access_token(user_login: schemas.UserLogin, db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, username=user_login.username)
    if not user or not crud.verify_password(user_login.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": user.api_key, "token_type": "bearer"}

@app.post("/icons/", response_model=schemas.Icon)
def create_icon(icon: schemas.IconCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return crud.create_icon(db=db, icon=icon)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/apps/", response_model=schemas.App)
def create_app(app: schemas.AppCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    analysis_results = security.analyze_app(db, app)
    icon_hash_str = None
    if app.icon_b64:
        try:
            image_data = base64.b64decode(app.icon_b64)
            image = Image.open(io.BytesIO(image_data))
            icon_hash_str = str(average_hash(image))
        except Exception as e:
            print(f"Error processing icon: {e}")

    db_app = models.App(
        name=app.name,
        package_name=app.package_name,
        icon_hash=icon_hash_str,
        is_clone=analysis_results["is_clone"],
        is_fake=analysis_results["is_fake"],
    )
    db.add(db_app)
    db.commit()
    db.refresh(db_app)
    return db_app

@app.post("/apps/bulk", response_model=List[schemas.App])
def create_apps(apps: schemas.AppBulkCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    created_apps = []
    all_icons = crud.get_all_icons(db)
    for app in apps.apps:
        analysis_results = security.analyze_app(db, app, all_icons)
        icon_hash_str = None
        if app.icon_b64:
            try:
                image_data = base64.b64decode(app.icon_b64)
                image = Image.open(io.BytesIO(image_data))
                icon_hash_str = str(average_hash(image))
            except Exception as e:
                print(f"Error processing icon: {e}")
        db_app = models.App(
            name=app.name,
            package_name=app.package_name,
            icon_hash=icon_hash_str,
            is_clone=analysis_results["is_clone"],
            is_fake=analysis_results["is_fake"],
        )
        db.add(db_app)
        created_apps.append(db_app)
    db.commit()
    for app in created_apps:
        db.refresh(app)
    return created_apps

@app.get("/apps/", response_model=List[schemas.App])
def read_apps(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    apps = db.query(models.App).offset(skip).limit(limit).all()
    return apps

@app.get("/apps/{app_id}", response_model=schemas.App)
def read_app(app_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_app = db.query(models.App).filter(models.App.id == app_id).first()
    if db_app is None:
        raise HTTPException(status_code=404, detail="App not found")
    return db_app

@app.post("/apps/{app_id}/permissions/", response_model=schemas.Permission)
def create_permission_for_app(
    app_id: int, permission: schemas.PermissionCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)
):
    db_app = db.query(models.App).filter(models.App.id == app_id).first()
    if db_app is None:
        raise HTTPException(status_code=404, detail="App not found")
    db_permission = models.Permission(**permission.dict(), app_id=app_id)
    db.add(db_permission)
    db.commit()
    db.refresh(db_permission)
    return db_permission

@app.post("/apps/{app_id}/api_calls/", response_model=schemas.ApiCall)
def create_api_call_for_app(
    app_id: int, api_call: schemas.ApiCallCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)
):
    db_app = db.query(models.App).filter(models.App.id == app_id).first()
    if db_app is None:
        raise HTTPException(status_code=404, detail="App not found")
    analysis_results = security.analyze_api_call(api_call)
    db_api_call = models.ApiCall(
        **api_call.dict(),
        app_id=app_id,
        risk_score=analysis_results["risk_score"],
        is_suspicious=analysis_results["is_suspicious"]
    )
    db.add(db_api_call)
    db.commit()
    db.refresh(db_api_call)
    return db_api_call

@app.post("/apps/{app_id}/device_health/", response_model=schemas.DeviceHealth)
def create_device_health_for_app(
    app_id: int, device_health: schemas.DeviceHealthCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)
):
    db_app = db.query(models.App).filter(models.App.id == app_id).first()
    if db_app is None:
        raise HTTPException(status_code=404, detail="App not found")
    analysis_results = security.analyze_device_health(device_health.dict())
    db_device_health = models.DeviceHealth(
        **device_health.dict(),
        app_id=app_id,
        risk_score=analysis_results["risk_score"],
        is_compromised=analysis_results["is_compromised"]
    )
    db.add(db_device_health)
    db.commit()
    db.refresh(db_device_health)
    return db_device_health

@app.post("/apps/{app_id}/network_traffic/", response_model=schemas.NetworkTraffic)
async def create_network_traffic_for_app(
    app_id: int, network_traffic: schemas.NetworkTrafficCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)
):
    db_app = db.query(models.App).filter(models.App.id == app_id).first()
    if db_app is None:
        raise HTTPException(status_code=404, detail="App not found")
    analysis_results = security.analyze_network_traffic(network_traffic.dict())
    db_network_traffic = models.NetworkTraffic(
        **network_traffic.dict(),
        app_id=app_id,
        risk_score=analysis_results["risk_score"],
        is_suspicious=analysis_results["is_suspicious"]
    )
    db.add(db_network_traffic)
    db.commit()
    db.refresh(db_network_traffic)
    if db_network_traffic.is_suspicious:
        await manager.broadcast(f"Suspicious network traffic detected from {db_network_traffic.destination_ip} for app {db_app.name}")
    return db_network_traffic

@app.post("/apps/{app_id}/urls/", response_model=schemas.Url)
def create_url_for_app(
    app_id: int, url: schemas.UrlCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)
):
    db_app = db.query(models.App).filter(models.App.id == app_id).first()
    if db_app is None:
        raise HTTPException(status_code=404, detail="App not found")
    analysis_results = security.analyze_url_for_phishing(url)
    db_url = models.Url(
        **url.dict(),
        app_id=app_id,
        is_phishing=analysis_results["is_phishing"],
        risk_score=analysis_results["risk_score"],
    )
    db.add(db_url)
    db.commit()
    db.refresh(db_url)
    return db_url

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast(f"Client #{client_id} says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat")
