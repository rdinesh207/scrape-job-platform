import logging

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes_applicants import router as applicants_router
from app.api.routes_jobs import router as jobs_router
from app.config.settings import settings


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Job Platform API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(jobs_router, prefix="/jobs", tags=["jobs"])
app.include_router(applicants_router, prefix="/applicants", tags=["applicants"])


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_request, exc: RequestValidationError):
    safe_errors = [
        {
            "loc": err.get("loc"),
            "msg": err.get("msg"),
            "type": err.get("type"),
        }
        for err in exc.errors()
    ]
    logger.error("Request validation failed errors=%s", safe_errors)
    return JSONResponse(status_code=422, content={"detail": exc.errors()})


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
