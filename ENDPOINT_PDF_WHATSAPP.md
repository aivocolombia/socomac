# 📄 Endpoint para Envío de PDF por WhatsApp

## 🎯 **Descripción**
Endpoint implementado para enviar PDFs por WhatsApp usando WHAPI con validaciones completas y logging detallado.

## 🔧 **Especificaciones Técnicas**

### **Endpoint Principal**
```
POST /whatsapp/enviar-pdf
```

### **URL WHAPI**
```
https://gate.whapi.cloud/messages/document
```

### **Variables de Entorno Requeridas**
```env
WHAPI_TOKEN=tu_token_whapi_aqui
WHAPI_BASE_URL=https://gate.whapi.cloud
```

## 📋 **Estructura del Request**

### **Headers**
```json
{
  "Content-Type": "application/json",
  "Accept": "application/json"
}
```

### **Body**
```json
{
  "numero_telefono": "+573172288329",
  "pdf_base64": "JVBERi0xLjQK...",
  "nombre_archivo": "recibo_caja_123_2025-01-18.pdf",
  "metadata": {
    "numero_recibo": 123,
    "empresa": "SOCOMAC",
    "cliente": "David Cuellar",
    "valor": "10000",
    "concepto": "Mercancia nacional",
    "fecha": "2025-01-18"
  }
}
```

## ✅ **Validaciones Implementadas**

### **1. Teléfono**
- ✅ Formato colombiano: `+57XXXXXXXXX`
- ✅ Regex: `^\+57\d{10}$`
- ✅ Validación en Pydantic

### **2. PDF Base64**
- ✅ Base64 válido
- ✅ Header PDF: `%PDF-`
- ✅ Tamaño máximo: 10MB
- ✅ Decodificación exitosa

### **3. Nombre de Archivo**
- ✅ Extensión `.pdf`
- ✅ Longitud máxima: 100 caracteres
- ✅ No vacío

## 📱 **Formato WHAPI**

### **Payload Enviado a WHAPI**
```json
{
  "to": "+573172288329",
  "type": "document",
  "document": {
    "filename": "recibo_caja_123_2025-01-18.pdf",
    "data": "JVBERi0xLjQK...",
    "mime_type": "application/pdf"
  },
  "caption": "📄 *Recibo de Caja SOCOMAC*\n\n📋 *Archivo:* recibo_caja_123_2025-01-18.pdf\n🔢 *Número de recibo:* 123\n🏢 *Empresa:* SOCOMAC\n👤 *Cliente:* David Cuellar\n💰 *Valor:* $10,000\n📝 *Concepto:* Mercancia nacional\n📅 *Fecha:* 2025-01-18\n\nEste es un recibo generado automáticamente."
}
```

## 📊 **Respuestas del Endpoint**

### **✅ Éxito (200)**
```json
{
  "success": true,
  "message": "PDF enviado exitosamente",
  "numero_telefono": "+573172288329",
  "archivo": "recibo_caja_123_2025-01-18.pdf",
  "tamaño_mb": 0.05,
  "metadata": {
    "numero_recibo": 123,
    "empresa": "SOCOMAC",
    "cliente": "David Cuellar",
    "valor": "10000",
    "concepto": "Mercancia nacional",
    "fecha": "2025-01-18"
  },
  "whapi_response": {
    "status": "success",
    "message_id": "wamid.xxx",
    "timestamp": "2025-01-18T10:30:00",
    "whatsapp_response": {...}
  }
}
```

### **❌ Error (400)**
```json
{
  "success": false,
  "detail": "Error específico del problema"
}
```

### **❌ Error (500)**
```json
{
  "success": false,
  "detail": "Error interno del servidor"
}
```

## 🔍 **Logging Detallado**

### **Logs de Entrada**
```
============================================================
📄 NUEVA SOLICITUD DE ENVÍO DE PDF
============================================================
📱 Teléfono destino: +573172288329
📄 Archivo: recibo_caja_123_2025-01-18.pdf
📊 Tamaño base64: 1234 caracteres
📋 Metadata: {'numero_recibo': 123, 'empresa': 'SOCOMAC'}
📏 Tamaño real del PDF: 0.05MB
💬 Mensaje personalizado: 📄 *Recibo de Caja SOCOMAC*...
🌐 URL WHAPI: https://gate.whapi.cloud/messages/document
🔑 Token configurado: Sí
🚀 Enviando PDF a WHAPI...
```

### **Logs de Respuesta**
```
📨 Respuesta WHAPI: {'status': 'success', 'message_id': 'wamid.xxx'}
✅ PDF enviado exitosamente a +573172288329
============================================================
```

### **Logs de Error**
```
❌ PDF demasiado grande: 15.2MB. Máximo permitido: 10MB
💥 Error inesperado enviando PDF: Connection timeout
============================================================
```

## 🧪 **Endpoints de Prueba**

### **1. Debug Configuración**
```
GET /whatsapp/debug-config
```

**Respuesta:**
```json
{
  "status": "success",
  "message": "Configuración de WHAPI",
  "config": {
    "whapi_base_url": "https://gate.whapi.cloud",
    "whapi_base_url_limpia": "https://gate.whapi.cloud",
    "whapi_token_configurado": true,
    "whapi_token_preview": "abc123def4...",
    "urls_generadas": {
      "mensaje": "https://gate.whapi.cloud/messages/text",
      "documento": "https://gate.whapi.cloud/messages/document",
      "status": "https://gate.whapi.cloud/status"
    }
  }
}
```

### **2. Endpoint Alternativo**
```
POST /whatsapp/enviar-pdf-alternativo
```

Prueba múltiples endpoints automáticamente si el principal falla.

## 🚀 **Cómo Usar**

### **1. Desde Frontend (JavaScript)**
```javascript
const enviarPDF = async (pdfBase64, telefono, metadata) => {
  try {
    const response = await fetch('https://socomac.onrender.com/whatsapp/enviar-pdf', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify({
        numero_telefono: telefono,
        pdf_base64: pdfBase64,
        nombre_archivo: `recibo_${metadata.numero_recibo}_${new Date().toISOString().split('T')[0]}.pdf`,
        metadata: metadata
      })
    });
    
    const result = await response.json();
    
    if (result.success) {
      console.log('✅ PDF enviado exitosamente');
      return result;
    } else {
      console.error('❌ Error:', result.detail);
      throw new Error(result.detail);
    }
  } catch (error) {
    console.error('❌ Error de conexión:', error);
    throw error;
  }
};
```

### **2. Desde cURL**
```bash
curl -X POST "https://socomac.onrender.com/whatsapp/enviar-pdf" \
  -H "Content-Type: application/json" \
  -d '{
    "numero_telefono": "+573172288329",
    "pdf_base64": "JVBERi0xLjQK...",
    "nombre_archivo": "recibo_123_2025-01-18.pdf",
    "metadata": {
      "numero_recibo": 123,
      "empresa": "SOCOMAC",
      "cliente": "David Cuellar",
      "valor": "10000",
      "concepto": "Mercancia nacional"
    }
  }'
```

## 🔧 **Configuración en Render**

### **Variables de Entorno**
```env
WHAPI_TOKEN=tu_token_whapi_aqui
WHAPI_BASE_URL=https://gate.whapi.cloud
FRONTEND_URL=https://tu-frontend.vercel.app
```

### **Build Command**
```bash
pip install -r requirements.txt
```

### **Start Command**
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

## 📝 **Notas Importantes**

1. **Timeout**: 30 segundos para requests a WHAPI
2. **Tamaño máximo**: 10MB por PDF
3. **Formato teléfono**: Obligatorio formato colombiano `+57XXXXXXXXX`
4. **Logging**: Detallado para debugging
5. **CORS**: Configurado para Vercel
6. **Validaciones**: Completas en Pydantic
7. **Manejo de errores**: Robusto con logging

## 🐛 **Debugging**

### **Problemas Comunes**

1. **Error 404**: Verificar URL WHAPI
2. **Error 400**: Validar formato de datos
3. **Error 500**: Revisar logs del servidor
4. **CORS**: Verificar configuración de orígenes

### **Herramientas de Debug**

1. **Endpoint debug**: `/whatsapp/debug-config`
2. **Logs detallados**: Revisar logs de Render
3. **Script de prueba**: `test_pdf_endpoint.py`

## 📚 **Archivos Relacionados**

- `app/api/whatsapp_endpoints.py` - Endpoints principales
- `app/services/whatsapp_service.py` - Servicio WHAPI
- `app/services/whatsapp_service_alternative.py` - Servicio alternativo
- `test_pdf_endpoint.py` - Script de pruebas
- `app/main.py` - Configuración CORS
