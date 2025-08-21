from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import get_settings
from src.core.database import init_db
from src.routers import admin, auth, content, profiles, reviews, streaming, subscriptions, users, watchlist

settings = get_settings()

openapi_tags = [
    {"name": "auth", "description": "User registration and login"},
    {"name": "users", "description": "User account endpoints"},
    {"name": "profiles", "description": "Multiple profiles per account"},
    {"name": "content", "description": "Browse and manage content"},
    {"name": "watchlist", "description": "Profile watchlist management"},
    {"name": "subscriptions", "description": "Plans and subscriptions"},
    {"name": "payments", "description": "Payment processing"},
    {"name": "reviews", "description": "Ratings and reviews"},
    {"name": "streaming", "description": "Secure playback endpoints"},
    {"name": "admin", "description": "Admin-only endpoints"},
]

app = FastAPI(
    title=settings.APP_NAME,
    description="CineStream Backend REST API",
    version=settings.APP_VERSION,
    openapi_tags=openapi_tags,
)

# CORS: Allow specific frontend origins and ensure preflight OPTIONS are handled
# Note: When allow_credentials=True, do not use "*" for allow_origins. The list is provided via env.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins(),
    allow_credentials=True,
    # Explicitly list common methods to ensure correct Access-Control-Allow-Methods on preflight
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    # Allow typical headers used by browsers on CORS/preflight, plus authorization
    allow_headers=[
        "Authorization",
        "Content-Type",
        "Accept",
        "Origin",
        "User-Agent",
        "X-Requested-With",
        "Accept-Language",
        "Accept-Encoding",
        "Cache-Control",
        "Pragma",
    ],
    expose_headers=["Content-Disposition"],
)

# Routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(profiles.router)
app.include_router(content.router)
app.include_router(watchlist.router)
app.include_router(subscriptions.router)
app.include_router(reviews.router)
app.include_router(streaming.router)
app.include_router(admin.router)


@app.get("/", tags=["auth"], summary="Health check")
def health_check():
    """Simple health check endpoint to verify the service is running."""
    return {"message": "Healthy"}


# Initialize DB on startup (safe if tables already exist)
@app.on_event("startup")
def on_startup():
    """Application startup hook: initialize database tables."""
    init_db()


# Allow running this module directly, defaulting to PORT env var or 3001
if __name__ == "__main__":
    import os
    import uvicorn

    uvicorn.run("src.api.main:app", host="0.0.0.0", port=int(os.getenv("PORT", "3001")), reload=False)
