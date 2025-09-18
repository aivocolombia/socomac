from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.webhook import router
from app.api.whatsapp_endpoints import router as whatsapp_router
import os

app = FastAPI(
    title="WhatsApp Integration API",
    description="API para integración con WhatsApp usando Whapi",
    version="1.0.0"
)

# Configurar CORS para permitir conexiones desde Vercel
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Desarrollo local
        "https://tu-app-vercel.vercel.app",  # Reemplaza con tu dominio de Vercel
        "https://*.vercel.app",  # Cualquier subdominio de Vercel
        os.getenv("FRONTEND_URL", "https://tu-app-vercel.vercel.app")  # Variable de entorno
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "status": "ok", 
        "message": "WhatsApp Integration API is alive",
        "version": "1.0.0",
        "endpoints": {
            "whatsapp": "/whatsapp",
            "webhook": "/webhook"
        }
    }

# Incluir routers
app.include_router(router)  # Webhook existente
app.include_router(whatsapp_router)  # Nuevos endpoints de WhatsApp