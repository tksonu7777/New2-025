from app.crud.base import CRUDBase
from app.models.screenshot import Screenshot
from app.schemas.screenshot import ScreenshotCreate, Screenshot


class CRUDScreenshot(CRUDBase[Screenshot, ScreenshotCreate, Screenshot]):
    pass


screenshot = CRUDScreenshot(Screenshot)
