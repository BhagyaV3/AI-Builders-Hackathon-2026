from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.ai import router as ai_router
from app.routes.forms import router as forms_router


app = FastAPI(
    title="AccessBridge API",
    description="Backend API for the AccessBridge form caseworker MVP",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health_check() -> dict:
    return {"status": "ok"}


app.include_router(forms_router, prefix="/api/forms", tags=["forms"])
app.include_router(ai_router, prefix="/api/ai", tags=["ai"])