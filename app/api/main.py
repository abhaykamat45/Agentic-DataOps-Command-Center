from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import settings
from app.core.db_metadata import metadata_db
from app.core.db_analytical import analytical_db
from app.core.synthetic_data import SyntheticDataGenerator
from app.api import (
    router_pipelines,
    router_incidents,
    router_agent,
    router_remediation,
    router_lineage,
    router_eval,
    router_audit
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure synthetic data is seeded if database is fresh
    try:
        pipes = metadata_db.fetch_all("SELECT * FROM pipelines")
        if not pipes:
            gen = SyntheticDataGenerator(metadata_db, analytical_db)
            gen.generate_all()
    except Exception:
        gen = SyntheticDataGenerator(metadata_db, analytical_db)
        gen.generate_all()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Agentic DataOps Command Center REST API",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(router_pipelines.router)
app.include_router(router_incidents.router)
app.include_router(router_agent.router)
app.include_router(router_remediation.router)
app.include_router(router_lineage.router)
app.include_router(router_eval.router)
app.include_router(router_audit.router)

@app.get("/")
def root():
    return {
        "status": "ONLINE",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "llm_provider": settings.LLM_PROVIDER
    }
