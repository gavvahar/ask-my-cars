from pathlib import Path

import plotly.io as pio
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .routes import ai_summary, dashboard, filters

# main.py sits at Python/backend/main.py -- templates/ and static/ live at the
# repo root (siblings of Python/), not nested under backend/, so this needs to
# resolve three levels up regardless of cwd (the Dockerfile runs uvicorn from
# WORKDIR /app/Python, not the repo root).
REPO_ROOT = Path(__file__).resolve().parents[2]

load_dotenv()

# Importing data_utils (via the routes above) imports streamlit, which as a
# side effect sets plotly's global default template to "streamlit" — a
# template with placeholder colors (#000001, #000002, ...) that Streamlit's
# own frontend swaps for real theme colors at render time. This process
# serves raw Plotly.js instead, so reset to plotly's normal template.
pio.templates.default = "plotly"

app = FastAPI(title="Car Specs & MPG Dashboard API")

app.include_router(filters.router)
app.include_router(dashboard.router)
app.include_router(ai_summary.router)

app.mount("/static", StaticFiles(directory=REPO_ROOT / "static"), name="static")

templates = Jinja2Templates(directory=REPO_ROOT / "templates")


@app.get("/")
def index(request: Request):
    return templates.TemplateResponse(request, "index.html")


@app.get("/health")
def health():
    return {"status": "ok"}
