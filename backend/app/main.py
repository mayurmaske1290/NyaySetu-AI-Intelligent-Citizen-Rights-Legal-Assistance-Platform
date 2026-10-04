from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import action_safety, analyze, authorities, claims, complaints, evidence, health, incidents, legal, rag, timeline
from app.core.config import settings
from app.core.errors import ControlledError, controlled_error_handler, generic_error_handler
from app.core.logging import configure_logging

configure_logging()

app = FastAPI(
    title="NyaySetu AI API",
    description=(
        "Phone-native AI rights and evidence protection assistant. "
        "Informational only — not legal advice. Demo knowledge is labeled."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(ControlledError, controlled_error_handler)
app.add_exception_handler(Exception, generic_error_handler)

PREFIX = "/api"
app.include_router(health.router, prefix=PREFIX)
app.include_router(analyze.router, prefix=PREFIX)
app.include_router(incidents.router, prefix=PREFIX)
app.include_router(evidence.router, prefix=PREFIX)
app.include_router(timeline.router, prefix=PREFIX)
app.include_router(claims.router, prefix=PREFIX)
app.include_router(action_safety.router, prefix=PREFIX)
app.include_router(complaints.router, prefix=PREFIX)
app.include_router(authorities.router, prefix=PREFIX)
app.include_router(rag.router, prefix=PREFIX)
app.include_router(legal.router, prefix=PREFIX)


@app.get("/")
async def root():
    return {
        "name": "NyaySetu AI",
        "tagline": "Know Your Rights. Protect Your Evidence. Take the Right Next Step.",
        "docs": "/docs",
        "health": "/api/health",
    }
