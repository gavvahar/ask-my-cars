from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .routes import ask

# main.py lives at Python/backend/main.py — templates/ and static/ are
# siblings of Python/ at the repo root (see Dockerfile: both are copied
# into /app alongside Python/), so three .parent hops from this file.
REPO_ROOT = Path(__file__).resolve().parent.parent.parent

app = FastAPI(title="Ask My Cars API")

app.include_router(ask.router)

app.mount("/static", StaticFiles(directory=REPO_ROOT / "static"), name="static")

templates = Jinja2Templates(directory=REPO_ROOT / "templates")


@app.get("/")
def index(request: Request):
    return templates.TemplateResponse(request, "index.html")


@app.get("/health")
def health():
    return {"status": "ok"}
