import os
from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from starlette.status import HTTP_403_FORBIDDEN
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

from app.note_app_routers import users, notes
from app import models, database, api_key_generator

BASE_DIR = Path(__file__).resolve().parent
env_path = BASE_DIR.parent / ".env"
load_dotenv(dotenv_path=env_path)

ADMIN_SECRET = os.getenv("ADMIN_SECRET")
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Notes App API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8001", "http://localhost:8001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_api_key(api_key: str = Security(api_key_header)):
    if api_key and api_key_generator.verify_api_key(api_key):
        return api_key
    raise HTTPException(
        status_code=HTTP_403_FORBIDDEN, detail="Could not validate API KEY"
    )

app.include_router(users.router)
app.include_router(notes.router)

@app.get("/")
def root():
    return {"message": "Welcome to Notes App!"}


@app.post("/generate-api-key")
def generate_api_key_endpoint():
    api_key = api_key_generator.generate_api_key_string()
    api_key_generator.save_api_key_to_db(api_key, owner="felix")
    return {"api_key": api_key}

# PROTECTED ENDPOINTS - Swagger UI requires API key - Protect this in production
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui(api_key: str = Depends(get_api_key)):
    return get_swagger_ui_html(openapi_url=app.openapi_url, title=app.title + " - Docs")

@app.get("/redoc", include_in_schema=False)
async def custom_redoc(api_key: str = Depends(get_api_key)):
    return get_redoc_html(openapi_url=app.openapi_url, title=app.title + " - ReDoc")

@app.get("/openapi.json", include_in_schema=False)
async def openapi_json(api_key: str = Depends(get_api_key)):
    return app.openapi()

