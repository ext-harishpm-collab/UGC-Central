from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .db.session import Base,engine
from .models import *
from .migrations import ensure_local_schema
from .api.routes import router as api_router
from .api.monthly_routes import router as monthly_router
from .api.reference_routes import router as reference_router
from .api.final_routes import router as final_router
from .api.uwt_final_routes import router as uwt_final_router
from .api.close_routes import router as close_router
from .api.parity_routes import router as parity_router
app=FastAPI(title="Creator Payout Control Tower",version="0.24.0")
Base.metadata.create_all(bind=engine)
ensure_local_schema()
app.add_middleware(CORSMiddleware,allow_origins=["*"],allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
app.include_router(api_router,prefix="/api")
app.include_router(monthly_router,prefix="/api")
app.include_router(reference_router,prefix="/api")
app.include_router(final_router,prefix="/api")
app.include_router(uwt_final_router,prefix="/api")
app.include_router(close_router,prefix="/api")
app.include_router(parity_router,prefix="/api")
@app.get("/")
def root():return {"service":"Creator Payout Control Tower","status":"ok","phase":24}
