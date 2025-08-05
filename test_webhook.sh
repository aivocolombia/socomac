#!/bin/bash

# Script para probar el webhook de Pascal AI Assistant

echo "Probando el endpoint raíz..."
curl -X GET http://localhost:8000/

echo -e "\n\nProbando el webhook con un mensaje de prueba..."
curl -X POST http://localhost:8000/api/v1/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hola, estoy buscando una propiedad",
    "phone": "+1234567890",
    "email": "test@example.com"
  }'

echo -e "\n\nProbando con información de ubicación..."
curl -X POST http://localhost:8000/api/v1/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Me interesa el barrio de Palermo",
    "phone": "+1234567890",
    "email": "test@example.com"
  }'

echo -e "\n\nProbando con presupuesto..."
curl -X POST http://localhost:8000/api/v1/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Mi presupuesto es de $2000 USD por mes",
    "phone": "+1234567890",
    "email": "test@example.com"
  }' 