from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.dev_routes import router as dev_router
from app.api.live_routes import router as live_router
from app.api.auth_routes import router as auth_router

app = FastAPI()

# CORS CONFIGURATION
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ROUTES
app.include_router(dev_router)
app.include_router(live_router)

app.include_router(auth_router)