from fastapi import FastAPI

from .routes import ask

app = FastAPI(title="Ask My Cars API")

app.include_router(ask.router)


@app.get("/health")
def health():
    return {"status": "ok"}
