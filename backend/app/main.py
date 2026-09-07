from fastapi import FastAPI

from app.routes.forms import router as forms_router


app = FastAPI(
    title="AccessBridge API",
    description="Backend API for the AccessBridge form caseworker MVP",
    version="0.1.0",
)


@app.get("/api/health")
def health_check() -> dict:
    return {"status": "ok"}


app.include_router(forms_router, prefix="/api/forms", tags=["forms"])