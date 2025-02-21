# File: backend/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

from app.core.config import settings
from app.api.v1.api import api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="""
    OPiN (Oracle Pi Network) API
    
    A decentralized data & services marketplace where Pi users can monetize their anonymized data 
    or perform microtasks for companies, while enterprises pay in Pi to access verified, real-time insights.
    
    ## Key Features
    
    * Data Submission and Validation
    * Real-time Data Processing
    * Privacy-Preserving Data Sharing
    * Enterprise Data Access
    * Subscription Management
    * User Authentication and Authorization
    
    ## Authentication
    
    The API uses JWT tokens for authentication. To authenticate:
    
    1. Get a token using the `/auth/login` endpoint
    2. Include the token in the `Authorization` header: `Bearer <token>`
    
    ## Rate Limiting
    
    API endpoints are rate-limited based on user tier:
    * Basic: 1000 requests/day
    * Premium: 10000 requests/day
    * Enterprise: 100000 requests/day
    """,
    version="1.0.0",
    openapi_url="/api/v1/openapi.json",
    docs_url=None,
    redoc_url=None,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # Custom OAuth2 schema
    openapi_schema["components"]["securitySchemes"] = {
        "JWT": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Enter JWT token"
        },
        "APIKey": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key",
            "description": "Enter API key"
        }
    }

    # Security requirement for all routes
    openapi_schema["security"] = [
        {"JWT": []},
        {"APIKey": []}
    ]

    # Add API status codes
    for path in openapi_schema["paths"].values():
        for method in path.values():
            if "responses" not in method:
                method["responses"] = {}

            method["responses"].update({
                "401": {
                    "description": "Authentication failed"
                },
                "403": {
                    "description": "Permission denied"
                },
                "429": {
                    "description": "Rate limit exceeded"
                }
            })

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Custom documentation endpoints
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
    )

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": app.version,
        "environment": settings.ENVIRONMENT
    }

# File: backend/app/api/v1/api.py

from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth,
    users,
    data_points,
    subscriptions,
    api_keys
)

api_router = APIRouter()

api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["authentication"]
)

api_router.include_router(
    users.router,
    prefix="/users",
    tags=["users"]
)

api_router.include_router(
    data_points.router,
    prefix="/data",
    tags=["data"]
)

api_router.include_router(
    subscriptions.router,
    prefix="/subscriptions",
    tags=["subscriptions"]
)

api_router.include_router(
    api_keys.router,
    prefix="/api-keys",
    tags=["api-keys"]
)

