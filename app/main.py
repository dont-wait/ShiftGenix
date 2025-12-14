from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routers import web, api

app = FastAPI(
    title="ShiftGenix",
    description="Genetic Algorithm based Shift Scheduling System",
    version="0.1.0"
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(web.router)
app.include_router(api.router, prefix="/api/v1")

@app.get("/health")
def health_check():
    return {"status": "ok"}
