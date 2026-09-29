from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .db.session import Base, engine
from .models import *  # noqa: F401,F403
from .api.routes import router

app = FastAPI(title="Creator Payout Control Tower", version="0.2.0")

Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

@app.get("/")
def root():
    return {"service": "Creator Payout Control Tower", "phase": 2, "status": "ok"}
