from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.webhook import router
from app.api.whatsapp_endpoints import router as whatsapp_router
from app.api.test_pdf_endpoint import router as test_pdf_router
import os

app = FastAPI(
    title="WhatsApp Integration API",
    description="API para integración con WhatsApp usando Whapi",
    version="1.0.0"
)

# Configurar CORS para permitir conexiones desde Vercel
# TEMPORAL: Configuración más permisiva para debugging
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*",  # TEMPORAL: Permitir todos los orígenes para debugging
        "http://localhost:3000",  # Desarrollo local
        "https://socomac-truck-pos-x3av-4p23q78xl-davids-projects-dc42c934.vercel.app",  # Tu dominio real de Vercel
        "https://*.vercel.app",  # Cualquier subdominio de Vercel
        "https://socomac-truck-pos.vercel.app",  # Dominio alternativo
        os.getenv("FRONTEND_URL", "https://socomac-truck-pos-x3av-4p23q78xl-davids-projects-dc42c934.vercel.app")  # Variable de entorno
    ],
    allow_credentials=False,  # TEMPORAL: Deshabilitar credentials para debugging
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
app.include_router(test_pdf_router)  # Endpoint de prueba PDF fijo