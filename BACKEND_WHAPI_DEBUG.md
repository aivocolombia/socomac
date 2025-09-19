# 🔧 Backend WHAPI con Debugging Completo

## 🎯 **Problemas Identificados**

### **1. Formato de Teléfono**
- ❌ **Problema**: Frontend envía `573172288329` (sin +57)
- ✅ **Solución**: Formateo automático a `+573172288329`

### **2. PDF Generado por jsPDF**
- ❌ **Problema**: PDF puede no ser válido
- ✅ **Solución**: Validación robusta del header PDF

### **3. Logging Insuficiente**
- ❌ **Problema**: Difícil debugging
- ✅ **Solución**: Logging detallado con emojis

## 🔧 **Implementación Mejorada**

### **1. Formateo Automático de Teléfono**
```python
def formatear_telefono_colombia(telefono: str) -> str:
    """
    Formatear teléfono colombiano automáticamente
    """
    # Remover espacios, guiones, paréntesis
    telefono_limpio = re.sub(r'[\s\-\(\)]', '', telefono)
    
    # Si empieza con 57, agregar +
    if telefono_limpio.startswith('57') and len(telefono_limpio) == 12:
        return f"+{telefono_limpio}"
    
    # Si empieza con +57, mantener
    if telefono_limpio.startswith('+57') and len(telefono_limpio) == 13:
        return telefono_limpio
    
    # Si empieza con 3, agregar +57
    if telefono_limpio.startswith('3') and len(telefono_limpio) == 10:
        return f"+57{telefono_limpio}"
    
    # Si es de 10 dígitos, agregar +57
    if len(telefono_limpio) == 10 and telefono_limpio.isdigit():
        return f"+57{telefono_limpio}"
    
    raise ValueError(f"Formato de teléfono inválido: {telefono}")
```

### **2. Validación Robusta de PDF**
```python
def validar_pdf_robusto(pdf_base64: str) -> Dict[str, Any]:
    """
    Validar PDF de manera robusta
    """
    try:
        # Decodificar base64
        pdf_bytes = base64.b64decode(pdf_base64)
        
        # Validar header PDF
        if not pdf_bytes.startswith(b'%PDF-'):
            return {
                "valido": False,
                "error": "No es un PDF válido (header incorrecto)",
                "header": pdf_bytes[:10]
            }
        
        # Validar tamaño
        size_mb = len(pdf_bytes) / (1024 * 1024)
        if size_mb > 10:
            return {
                "valido": False,
                "error": f"PDF demasiado grande: {size_mb:.2f}MB",
                "tamaño_mb": size_mb
            }
        
        # Validar que tenga contenido mínimo
        if len(pdf_bytes) < 100:
            return {
                "valido": False,
                "error": "PDF demasiado pequeño",
                "tamaño_bytes": len(pdf_bytes)
            }
        
        return {
            "valido": True,
            "tamaño_mb": round(size_mb, 2),
            "tamaño_bytes": len(pdf_bytes),
            "header": pdf_bytes[:10].decode('utf-8', errors='ignore')
        }
        
    except Exception as e:
        return {
            "valido": False,
            "error": f"Error validando PDF: {str(e)}"
        }
```

### **3. Logging Detallado**
```python
def log_solicitud_pdf(request: PDFRequest):
    """
    Logging detallado de la solicitud
    """
    logger.info("=" * 80)
    logger.info("📄 NUEVA SOLICITUD DE ENVÍO DE PDF")
    logger.info("=" * 80)
    logger.info(f"📱 Teléfono original: {request.numero_telefono}")
    logger.info(f"📄 Archivo: {request.nombre_archivo}")
    logger.info(f"📊 Tamaño base64: {len(request.pdf_base64)} caracteres")
    logger.info(f"📋 Metadata: {request.metadata}")
    
    # Validar PDF
    validacion = validar_pdf_robusto(request.pdf_base64)
    if validacion["valido"]:
        logger.info(f"✅ PDF válido: {validacion['tamaño_mb']}MB")
    else:
        logger.error(f"❌ PDF inválido: {validacion['error']}")
    
    # Formatear teléfono
    try:
        telefono_formateado = formatear_telefono_colombia(request.numero_telefono)
        logger.info(f"📱 Teléfono formateado: {telefono_formateado}")
    except Exception as e:
        logger.error(f"❌ Error formateando teléfono: {e}")
```

### **4. Endpoint Mejorado**
```python
@router.post("/enviar-pdf")
async def enviar_pdf_whatsapp_mejorado(
    request: PDFRequest,
    whatsapp_service: WhatsAppService = Depends(get_whatsapp_service)
):
    """
    Endpoint mejorado para enviar PDF con debugging completo
    """
    try:
        # 🔍 LOGGING DETALLADO
        log_solicitud_pdf(request)
        
        # ✅ FORMATEAR TELÉFONO
        try:
            telefono_formateado = formatear_telefono_colombia(request.numero_telefono)
            logger.info(f"📱 Teléfono formateado: {telefono_formateado}")
        except Exception as e:
            error_msg = f"Error formateando teléfono: {str(e)}"
            logger.error(f"❌ {error_msg}")
            raise HTTPException(status_code=400, detail=error_msg)
        
        # ✅ VALIDAR PDF
        validacion = validar_pdf_robusto(request.pdf_base64)
        if not validacion["valido"]:
            error_msg = f"PDF inválido: {validacion['error']}"
            logger.error(f"❌ {error_msg}")
            raise HTTPException(status_code=400, detail=error_msg)
        
        logger.info(f"✅ PDF válido: {validacion['tamaño_mb']}MB")
        
        # ✅ CREAR MENSAJE PERSONALIZADO
        mensaje_personalizado = crear_mensaje_pdf(request.metadata, request.nombre_archivo)
        logger.info(f"💬 Mensaje: {mensaje_personalizado}")
        
        # ✅ ENVIAR A WHAPI
        logger.info("🚀 Enviando a WHAPI...")
        resultado = whatsapp_service.enviar_documento_base64(
            telefono_formateado,  # Usar teléfono formateado
            request.pdf_base64,
            request.nombre_archivo,
            mensaje_personalizado
        )
        
        # 📊 RESPUESTA
        logger.info(f"📨 Respuesta WHAPI: {resultado}")
        
        if "error" in resultado:
            error_msg = f"Error WHAPI: {resultado['error']}"
            logger.error(f"❌ {error_msg}")
            raise HTTPException(status_code=400, detail=error_msg)
        
        # ✅ ÉXITO
        logger.info(f"✅ PDF enviado exitosamente a {telefono_formateado}")
        logger.info("=" * 80)
        
        return {
            "success": True,
            "message": "PDF enviado exitosamente",
            "numero_telefono": telefono_formateado,
            "archivo": request.nombre_archivo,
            "tamaño_mb": validacion["tamaño_mb"],
            "metadata": request.metadata,
            "whapi_response": resultado
        }
        
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Error inesperado: {str(e)}"
        logger.error(f"💥 {error_msg}")
        logger.error("=" * 80)
        raise HTTPException(status_code=500, detail="Error interno del servidor")
```

### **5. Endpoints de Prueba**
```python
@router.post("/test-pdf")
async def test_pdf_endpoint():
    """
    Endpoint para probar la funcionalidad de PDF
    """
    # Crear PDF de prueba
    pdf_prueba = crear_pdf_prueba()
    pdf_base64 = base64.b64encode(pdf_prueba).decode('utf-8')
    
    return {
        "message": "PDF de prueba creado",
        "tamaño_bytes": len(pdf_prueba),
        "tamaño_base64": len(pdf_base64),
        "header": pdf_prueba[:10].decode('utf-8', errors='ignore')
    }

@router.post("/test-telefono")
async def test_telefono_endpoint(telefono: str):
    """
    Endpoint para probar formateo de teléfono
    """
    try:
        telefono_formateado = formatear_telefono_colombia(telefono)
        return {
            "original": telefono,
            "formateado": telefono_formateado,
            "valido": True
        }
    except Exception as e:
        return {
            "original": telefono,
            "error": str(e),
            "valido": False
        }
```

## 🧪 **Script de Prueba Completo**

```python
#!/usr/bin/env python3
"""
Script de prueba completo para debugging
"""
import requests
import base64
import json

def test_formateo_telefono():
    """
    Probar formateo de teléfono
    """
    print("🧪 Probando formateo de teléfono...")
    
    telefonos_prueba = [
        "573172288329",
        "+573172288329", 
        "3172288329",
        "3172288329",
        "573172288329"
    ]
    
    for telefono in telefonos_prueba:
        try:
            response = requests.post(
                "https://socomac.onrender.com/whatsapp/test-telefono",
                json={"telefono": telefono}
            )
            result = response.json()
            print(f"📱 {telefono} -> {result.get('formateado', 'ERROR')}")
        except Exception as e:
            print(f"❌ Error con {telefono}: {e}")

def test_pdf_endpoint():
    """
    Probar endpoint de PDF
    """
    print("\n🧪 Probando endpoint de PDF...")
    
    # Crear PDF de prueba
    pdf_content = crear_pdf_prueba()
    pdf_base64 = base64.b64encode(pdf_content).decode('utf-8')
    
    payload = {
        "numero_telefono": "573172288329",  # Sin +57
        "pdf_base64": pdf_base64,
        "nombre_archivo": "test_recibo_123.pdf",
        "metadata": {
            "numero_recibo": 123,
            "empresa": "SOCOMAC",
            "cliente": "David Cuellar",
            "valor": "10000"
        }
    }
    
    try:
        response = requests.post(
            "https://socomac.onrender.com/whatsapp/enviar-pdf",
            json=payload
        )
        
        print(f"📊 Status: {response.status_code}")
        print(f"📄 Response: {response.json()}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """
    Ejecutar todas las pruebas
    """
    print("🚀 INICIANDO PRUEBAS DE DEBUGGING")
    print("=" * 60)
    
    test_formateo_telefono()
    test_pdf_endpoint()
    
    print("\n✅ Pruebas completadas")

if __name__ == "__main__":
    main()
```

## 📋 **Checklist de Implementación**

- [ ] ✅ Formateo automático de teléfono
- [ ] ✅ Validación robusta de PDF
- [ ] ✅ Logging detallado
- [ ] ✅ Endpoints de prueba
- [ ] ✅ Manejo de errores mejorado
- [ ] ✅ Script de prueba completo
- [ ] ✅ Documentación actualizada

## 🚀 **Próximos Pasos**

1. **Implementar** las mejoras en el código
2. **Probar** con el script de debugging
3. **Verificar** logs en Render
4. **Integrar** en el frontend
5. **Monitorear** funcionamiento en producción
