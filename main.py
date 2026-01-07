import threading
from scheduler import scheduler_loop
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db import Base, engine
from api import router as api_router
from scheduler import start_scheduler
from websocket import websocket_endpoint

# -------------------------
# APP INIT
# -------------------------
app = FastAPI(
    title="Taco Factory Production System",
    version="1.0"
)

# -------------------------
# CORS (frontend ready)
# -------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # later restrict
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# DATABASE INIT
# -------------------------
Base.metadata.create_all(bind=engine)

# -------------------------
# START BACKGROUND SCHEDULER
# -------------------------
@app.on_event("startup")
def startup_event():
    start_scheduler()

# -------------------------
# ROOT TEST ROUTE
# -------------------------
@app.get("/")
def root():
    return {
        "status": "Backend running",
        "service": "Taco Factory Production System",
        "version": "1.0"
    }

# -------------------------
# API ROUTES
# -------------------------
app.include_router(api_router, prefix="/api")

# -------------------------
# WEBSOCKET (REAL-TIME)
# -------------------------
@app.websocket("/ws")
async def websocket_route(websocket):
    await websocket_endpoint(websocket)
