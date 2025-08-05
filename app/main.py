from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.webhook import router

app = FastAPI()



@app.get("/")
def root():
    return {"status": "ok", "message": "Root endpoint is alive"}
app.include_router(router)