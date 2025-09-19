# 📁 Integración con Supabase Storage

## 🎯 **Descripción**
Integración completa de Supabase Storage con WHAPI para envío de PDFs por WhatsApp.

## ✅ **Ventajas de Supabase Storage:**

### **1. 📁 Almacenamiento Persistente**
- Los PDFs se guardan permanentemente
- Acceso desde cualquier lugar
- Historial completo de documentos

### **2. 🔗 URLs Públicas**
- URLs directas a los archivos
- Fácil integración con WHAPI
- Sin límites de tamaño

### **3. 📊 Gestión Avanzada**
- Listado de documentos
- Eliminación de archivos
- Metadatos personalizados

## 🔧 **Configuración Requerida:**

### **Variables de Entorno:**
```env
# WHAPI
WHAPI_TOKEN=tu_token_whapi_aqui
WHAPI_BASE_URL=https://gate.whapi.cloud

# Supabase
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_ANON_KEY=tu_anon_key_aqui
```

### **Instalación:**
```bash
pip install supabase>=2.0.0
```

## 📋 **Endpoints Disponibles:**

### **1. Envío con Supabase Storage**
```
POST /whatsapp/enviar-pdf-supabase
```

**Request:**
```json
{
  "numero_telefono": "573172288329",
  "pdf_base64": "JVBERi0xLjQK...",
  "nombre_archivo": "recibo_123_2025-01-18.pdf",
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

**Response:**
```json
{
  "success": true,
  "message": "PDF enviado exitosamente (Supabase Storage)",
  "numero_telefono": "+573172288329",
  "archivo": "recibo_123_2025-01-18.pdf",
  "tamaño_mb": 0.05,
  "url_supabase": "https://tu-proyecto.supabase.co/storage/v1/object/public/documentos-whatsapp/20250118_12345678_recibo_123_2025-01-18.pdf",
  "metadata": {...},
  "supabase_result": {...},
  "whatsapp_result": {...}
}
```

### **2. Listar Documentos**
```
GET /whatsapp/documentos-supabase?limite=50
```

**Response:**
```json
{
  "status": "success",
  "archivos": [
    {
      "name": "20250118_12345678_recibo_123.pdf",
      "size": 1024,
      "created_at": "2025-01-18T10:30:00Z"
    }
  ],
  "total": 1
}
```

### **3. Eliminar Documento**
```
DELETE /whatsapp/documentos-supabase/{nombre_archivo}
```

**Response:**
```json
{
  "success": true,
  "message": "Documento 20250118_12345678_recibo_123.pdf eliminado"
}
```

## 🔄 **Flujo de Envío:**

### **Paso 1: Subir a Supabase Storage**
```python
# Subir PDF a Supabase
upload_result = supabase_service.subir_pdf(
    pdf_base64, 
    nombre_archivo, 
    metadata
)

# Obtener URL pública
url_publica = upload_result["url_publica"]
```

### **Paso 2: Enviar por WhatsApp**
```python
# Enviar usando URL de Supabase
whatsapp_result = whatsapp_service.enviar_documento(
    numero_telefono,
    url_publica,  # URL de Supabase
    nombre_archivo,
    mensaje
)
```

## 📊 **Comparación de Métodos:**

| Aspecto | Directo (WHAPI) | Supabase + WHAPI |
|---------|----------------|-------------------|
| **Velocidad** | ⚡ Rápido | 🐌 Más lento |
| **Almacenamiento** | ❌ Temporal | ✅ Permanente |
| **Historial** | ❌ No | ✅ Sí |
| **Reutilización** | ❌ No | ✅ Sí |
| **URLs** | ❌ No | ✅ Sí |
| **Gestión** | ❌ Limitada | ✅ Completa |
| **Costo** | 🟢 Gratis | 🟡 Storage |

## 🧪 **Pruebas:**

### **Script de Prueba:**
```bash
python test_supabase_integration.py
```

### **Pruebas Manuales:**
```bash
# Envío con Supabase
curl -X POST "https://socomac.onrender.com/whatsapp/enviar-pdf-supabase" \
  -H "Content-Type: application/json" \
  -d '{
    "numero_telefono": "573172288329",
    "pdf_base64": "JVBERi0xLjQK...",
    "nombre_archivo": "test.pdf",
    "metadata": {"cliente": "Test"}
  }'

# Listar documentos
curl "https://socomac.onrender.com/whatsapp/documentos-supabase"

# Eliminar documento
curl -X DELETE "https://socomac.onrender.com/whatsapp/documentos-supabase/archivo.pdf"
```

## 🔧 **Configuración en Supabase:**

### **1. Crear Bucket:**
```sql
-- El bucket se crea automáticamente
-- Nombre: "documentos-whatsapp"
-- Público: true
```

### **2. Tabla de Metadatos (Opcional):**
```sql
CREATE TABLE documentos_whatsapp (
  id SERIAL PRIMARY KEY,
  nombre_archivo TEXT NOT NULL,
  url_publica TEXT NOT NULL,
  metadata JSONB,
  fecha_creacion TIMESTAMP DEFAULT NOW(),
  tipo TEXT DEFAULT 'pdf_whatsapp'
);
```

### **3. Políticas de Seguridad:**
```sql
-- Permitir lectura pública
CREATE POLICY "Public read access" ON storage.objects
FOR SELECT USING (bucket_id = 'documentos-whatsapp');

-- Permitir escritura autenticada
CREATE POLICY "Authenticated write access" ON storage.objects
FOR INSERT WITH CHECK (bucket_id = 'documentos-whatsapp');
```

## 📱 **Frontend:**

### **JavaScript:**
```javascript
// Envío con Supabase
const enviarPDFSupabase = async (pdfBase64, telefono, metadata) => {
  try {
    const response = await fetch('/whatsapp/enviar-pdf-supabase', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        numero_telefono: telefono,
        pdf_base64: pdfBase64,
        nombre_archivo: `recibo_${Date.now()}.pdf`,
        metadata: metadata
      })
    });
    
    const result = await response.json();
    
    if (result.success) {
      console.log('✅ PDF enviado con Supabase');
      console.log('🔗 URL:', result.url_supabase);
      return result;
    } else {
      throw new Error(result.detail);
    }
  } catch (error) {
    console.error('❌ Error:', error);
    throw error;
  }
};

// Listar documentos
const listarDocumentos = async () => {
  try {
    const response = await fetch('/whatsapp/documentos-supabase?limite=50');
    const result = await response.json();
    return result.archivos;
  } catch (error) {
    console.error('❌ Error listando documentos:', error);
    return [];
  }
};
```

## 🚀 **Despliegue:**

### **Render:**
```env
# Variables de entorno en Render
WHAPI_TOKEN=tu_token_whapi
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_ANON_KEY=tu_anon_key
```

### **Supabase:**
1. Crear proyecto en Supabase
2. Obtener URL y ANON_KEY
3. Configurar bucket "documentos-whatsapp"
4. Configurar políticas de seguridad

## 📝 **Archivos Creados:**

- ✅ `app/services/supabase_storage.py` - Servicio Supabase
- ✅ `app/services/whatsapp_supabase_service.py` - Servicio híbrido
- ✅ `app/api/whatsapp_endpoints.py` - Endpoints actualizados
- ✅ `test_supabase_integration.py` - Script de pruebas
- ✅ `requirements.txt` - Dependencia supabase
- ✅ `env_example.txt` - Variables de entorno

## 🔍 **Logging:**

```
📤 Subiendo PDF a Supabase: recibo_123.pdf
✅ PDF subido a Supabase: https://tu-proyecto.supabase.co/storage/v1/object/public/documentos-whatsapp/20250118_12345678_recibo_123.pdf
📱 Enviando por WhatsApp...
✅ PDF enviado exitosamente por WhatsApp
```

## 💡 **Recomendaciones:**

1. **Para desarrollo**: Usar método directo (más rápido)
2. **Para producción**: Usar Supabase Storage (más robusto)
3. **Para historial**: Supabase Storage obligatorio
4. **Para reutilización**: Supabase Storage recomendado

¿Quieres que configure algún aspecto específico o necesitas ayuda con la configuración en Supabase?
