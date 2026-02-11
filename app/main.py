from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import search
import os
from dotenv import load_dotenv

from pathlib import Path
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

app = FastAPI(title="Retrieval Strategy Testing API")

# Configure CORS
# Configure CORS
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    print(f"DEBUG INCOMING: {request.method} {request.url}", flush=True)
    try:
        response = await call_next(request)
        print(f"DEBUG RESPONSE: {response.status_code}", flush=True)
        return response
    except Exception as e:
        print(f"DEBUG ERROR: {e}", flush=True)
        raise e

from fastapi import Request, status
from fastapi.responses import JSONResponse
import traceback

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    error_msg = str(exc)
    trace = traceback.format_exc()
    print(f"CRITICAL: Unhandled Exception in {request.url}: {error_msg}")
    print(trace, flush=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": error_msg, "traceback": trace},
    )

app.include_router(search.router, prefix="/api/search", tags=["search"])
from app.api.routes import stm
app.include_router(stm.router, prefix="/api/stm", tags=["stm"])

from app.api.routes import debug
app.include_router(debug.router, prefix="/api/debug", tags=["debug"])

from app.api.routes import adaptive_fusion_route
app.include_router(adaptive_fusion_route.router, prefix="/api/search")

@app.get("/")
def read_root():
    return {"message": "Retrieval Strategy Testing API is running"}

@app.get("/api/debug/error")
def trigger_error():
    raise Exception("Test Error for Middleware Verification")
