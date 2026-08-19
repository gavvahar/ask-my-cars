from pathlib import Path

import plotly.io as pio
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .routes import ai_summary, dashboard, filters

BASE_DIR = Path(__file__).resolve().parent

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

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

templates = Jinja2Templates(directory=BASE_DIR / "templates")


@app.get("/")
def index(request: Request):
    return templates.TemplateResponse(request, "index.html")


@app.get("/health")
def health():
    return {"status": "ok"}
