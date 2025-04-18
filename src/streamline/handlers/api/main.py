from fastapi import FastAPI

from streamline.config.settings import settings
from streamline.handlers.api.v1.metrics import router as metrics_router

app: FastAPI = FastAPI(
    title=settings.app.get('name'),
    version=settings.app.get('version'),
    docs_url='/',
)

app.include_router(metrics_router, prefix='/v1/metrics', tags=['metrics'])
