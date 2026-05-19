from fastapi import FastAPI

from app.api.dev_routes import router as dev_router

from app.api.live_routes import router as live_router


app = FastAPI()

app.include_router(dev_router)

app.include_router(live_router)