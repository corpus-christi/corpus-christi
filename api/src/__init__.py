from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import BASE_DIR, settings


BASE_DIR = BASE_DIR


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables if they don't exist
    from .db import Base, engine
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown


def create_app() -> FastAPI:
    """Application factory for the FastAPI app."""

    app = FastAPI(title="Corpus Christi API", lifespan=lifespan)

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Import and include all routers
    from .etc.api import router as etc_router
    app.include_router(etc_router)

    from .auth.api import router as auth_router
    app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])

    from .attributes.api import router as attributes_router
    app.include_router(attributes_router, prefix="/api/v1/attributes", tags=["attributes"])

    from .events.api import router as events_router
    app.include_router(events_router, prefix="/api/v1/events", tags=["events"])

    from .assets.api import router as assets_router
    app.include_router(assets_router, prefix="/api/v1/assets", tags=["assets"])

    from .teams.api import router as teams_router
    app.include_router(teams_router, prefix="/api/v1/teams", tags=["teams"])

    from .emails.api import router as emails_router
    app.include_router(emails_router, prefix="/api/v1/emails", tags=["emails"])

    from .groups.api import router as groups_router
    app.include_router(groups_router, prefix="/api/v1/groups", tags=["groups"])

    from .courses.api import router as courses_router
    app.include_router(courses_router, prefix="/api/v1/courses", tags=["courses"])

    from .i18n.api import router as i18n_router
    app.include_router(i18n_router, prefix="/api/v1/i18n", tags=["i18n"])

    from .people.api import router as people_router
    app.include_router(people_router, prefix="/api/v1/people", tags=["people"])

    from .places.api import router as places_router
    app.include_router(places_router, prefix="/api/v1/places", tags=["places"])

    from .images.api import router as images_router
    app.include_router(images_router, prefix="/api/v1/images", tags=["images"])

    return app
