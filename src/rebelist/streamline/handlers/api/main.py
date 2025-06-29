from fastapi import FastAPI

from rebelist.streamline.config.container import Container
from rebelist.streamline.handlers.api.metrics.flow import router as metrics_router

container = Container.create()
settings = container.settings()

app: FastAPI = FastAPI(
    title=settings.app.name,
    version=settings.app.version,
    docs_url='/',
)

app.include_router(metrics_router, prefix='/v1/metrics', tags=['metrics'])
app.state.container = container
