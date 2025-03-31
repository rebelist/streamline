# from streamline.backend import *

from fastapi import FastAPI

app = FastAPI()

# Register backend routes
# fastapi.include_router(user.router)


@app.get('/')
async def root():
    return {'message': 'Hello World'}
