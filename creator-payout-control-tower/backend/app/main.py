from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .db.session import Base,engine
from .models import *
from .migrations import ensure_local_schema
from .api.routes import router

app=FastAPI(title="Creator Payout Control Tower",version="0.14.1")
Base.metadata.create_all(bind=engine)
ensure_local_schema()
app.add_middleware(CORSMiddleware,allow_origins=["*"],allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
app.include_router(router,prefix="/api")

@app.get("/")
def root():
    return {"service":"Creator Payout Control Tower","status":"ok","phase":14}
