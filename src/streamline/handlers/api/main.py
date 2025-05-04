from fastapi import FastAPI

from streamline.config.container import Container
from streamline.handlers.api.v1.metrics import router as metrics_router

container = Container.create()
settings = container.settings()

app: FastAPI = FastAPI(
    title=settings.app.name,
    version=settings.app.version,
    docs_url='/',
)

app.include_router(metrics_router, prefix='/v1/metrics', tags=['metrics'])
app.state.container = container
