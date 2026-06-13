from fastapi import FastAPI

from backend.app.database import Base, engine
from backend.app.settings import ensure_data_dir, settings
from backend import models  # noqa: F401

app = FastAPI(title="ResumeFit API", version="0.1.0")


@app.on_event("startup")
def on_startup() -> None:
    ensure_data_dir(settings)
    Base.metadata.create_all(bind=engine)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
