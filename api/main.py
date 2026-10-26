import importlib
import logging
import time
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

from api.dependencies import (
    get_crop_indian_service,
    get_crop_service,
    get_disease_service,
    get_yield_service,
)
from api.routes import disease, crop, summary
yield_route = importlib.import_module("api.routes.yield")

# Setup logging config
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("api_server.log")
    ]
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load all models once on startup
    logging.info("Lifespan startup: Pre-loading ML model checkpoints...")
    try:
        get_disease_service()
        get_crop_service()
        get_crop_indian_service()
        get_yield_service()
        logging.info("All ML model checkpoints successfully pre-loaded in memory.")
    except Exception as e:
        logging.critical(f"Failed to pre-load model checkpoints: {str(e)}", exc_info=True)
    yield
    logging.info("Lifespan shutdown: Cleaning up serving services.")

app = FastAPI(
    title="CropAI serving API",
    description="Explainable, uncertainty-aware agricultural serving endpoints.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logger middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    duration = time.time() - start_time
    
    # Format log based on route matching
    path = request.url.path
    method = request.method
    status_code = response.status_code
    
    # Try to extract model version from request path
    model_ver = "unknown"
    if "disease" in path:
        model_ver = "disease_v1"
    elif "crop" in path:
        model_ver = "crop_v1"
    elif "yield" in path:
        model_ver = "yield_v1"
        
    logging.info(
        f"{method} {path} status={status_code} latency={duration:.4f}s model={model_ver}"
    )
    
    return response

# General exception handler (no trace leakage)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logging.error(f"Unhandled Exception at {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred. Please try again later."}
    )

# Mount endpoints
app.include_router(disease.router, prefix="/api/v1/disease", tags=["Disease Diagnosis"])
app.include_router(crop.router, prefix="/api/v1/crop", tags=["Crop Recommendation"])
app.include_router(yield_route.router, prefix="/api/v1/yield", tags=["Yield Prediction"])
app.include_router(summary.router, prefix="/api/v1/summary", tags=["Farmer Summaries"])

@app.get("/health")
async def health_check():
    def _check(loader):
        try:
            return loader() is not None
        except Exception:
            return False

    return {
        "status": "ok",
        "models_loaded": {
            "disease": _check(get_disease_service),
            "crop": _check(get_crop_service),
            "crop_indian": _check(get_crop_indian_service),
            "yield": _check(get_yield_service),
        }
    }
