# Herramienta: Identificar Administrador

## Descripción

La herramienta `identificar_administrador` permite al agente verificar si un número de teléfono pertenece a un administrador registrado en la tabla `user_agent` de Supabase.

## Funcionalidad

- **Verificación de permisos**: Identifica si un usuario tiene privilegios de administrador
- **Validación de formato**: Acepta números de teléfono en diferentes formatos
- **Consulta a Supabase**: Busca en la tabla `user_agent` con filtros `phone` y `type = "Administrador"`
- **Información detallada**: Retorna datos completos del administrador si existe

## Uso

### Sintaxis
```python
identificar_administrador(phone: str) -> str
```

### Parámetros
- `phone` (str): Número de teléfono a verificar (formato: 573xxxxxxxxx)

### Retorno
- **Si es administrador**: Información completa del administrador
- **Si no es administrador**: Mensaje de error indicando que no está registrado
- **Si hay error**: Mensaje de error descriptivo

## Formatos de Teléfono Soportados

La herramienta acepta números de teléfono en los siguientes formatos:
- `573195792747` (formato estándar)
- `573 195 792 747` (con espacios)
- `573-195-792-747` (con guiones)
- `+573195792747` (con símbolo +)

## Ejemplos de Uso

### Ejemplo 1: Verificar Administrador
```python
result = identificar_administrador("573195792747")
# Retorna información del administrador si existe
```

### Ejemplo 2: Verificar Usuario Regular
```python
result = identificar_administrador("573172288329")
# Retorna: "El número de teléfono 573172288329 no está registrado como administrador"
```

### Ejemplo 3: Formato con Espacios
```python
result = identificar_administrador("573 195 792 747")
# Limpia automáticamente el formato y verifica
```

## Integración con el Agente

### Flujo de Verificación
1. **Recepción de mensaje**: El webhook recibe un mensaje con número de teléfono
2. **Verificación de permisos**: Se llama a `identificar_administrador(phone)`
3. **Determinación de acceso**:
   - Si es administrador: Acceso completo a todas las herramientas
   - Si no es administrador: Acceso limitado a funcionalidades básicas

### Ejemplo de Integración
```python
def procesar_mensaje(phone: str, message: str):
    # Verificar si es administrador
    admin_check = identificar_administrador(phone)
    
    if "ADMINISTRADOR IDENTIFICADO" in admin_check:
        # Acceso completo
        return procesar_como_administrador(message)
    else:
        # Acceso limitado
        return procesar_como_usuario_regular(message)
```

## Estructura de la Tabla user_agent

La herramienta consulta la tabla `user_agent` en Supabase con la siguiente estructura:

```sql
SELECT * FROM user_agent 
WHERE phone = '573xxxxxxxxx' 
AND type = 'Administrador'
```

### Campos Esperados
- `id`: ID único del usuario
- `name`: Nombre del administrador
- `phone`: Número de teléfono
- `type`: Tipo de usuario (debe ser "Administrador")
- `email`: Correo electrónico
- `created_at`: Fecha de creación
- `updated_at`: Fecha de última actualización

## Validaciones

### Validación de Formato
- El número debe comenzar con "573"
- Debe tener exactamente 12 dígitos
- Se limpian automáticamente espacios, guiones y símbolos +

### Validación de Datos
- Verifica que el teléfono no esté vacío
- Valida el formato antes de consultar Supabase
- Maneja errores de conexión a la base de datos

## Mensajes de Error

### Errores de Validación
- `"Error: Debe proporcionar un número de teléfono válido."`
- `"Error: El número de teléfono debe tener el formato 573xxxxxxxxx"`

### Errores de Base de Datos
- `"Error al identificar administrador: [detalle del error]"`

### Usuario No Encontrado
- `"El número de teléfono [número] no está registrado como administrador"`

## Archivos Relacionados

- **Herramienta**: `app/core/tools.py` (función `identificar_administrador`)
- **Conexión Supabase**: `app/db/supabase.py`
- **Pruebas**: `test_identificar_administrador.py`
- **Ejemplo de uso**: `ejemplo_uso_identificar_administrador.py`

## Configuración Requerida

### Variables de Entorno
```env
SUPABASE_URL=tu_url_de_supabase
SUPABASE_KEY=tu_clave_de_supabase
```

### Dependencias
```python
from app.db.supabase import get_supabase_client
```

## Casos de Uso

### 1. Control de Acceso
- Restringir funcionalidades administrativas
- Permitir acceso completo solo a administradores
- Registrar intentos de acceso no autorizado

### 2. Personalización de Respuestas
- Adaptar respuestas según el nivel de permisos
- Mostrar información específica para administradores
- Ocultar funcionalidades sensibles a usuarios regulares

### 3. Auditoría
- Registrar qué administradores usan el sistema
- Rastrear acciones administrativas
- Mantener logs de acceso

## Mejoras Futuras

1. **Cache de verificación**: Almacenar resultados temporalmente
2. **Múltiples roles**: Soporte para diferentes tipos de usuario
3. **Logs detallados**: Registrar todas las verificaciones
4. **Notificaciones**: Alertar sobre intentos de acceso no autorizado
5. **Rate limiting**: Limitar verificaciones por minuto

## Troubleshooting

### Problemas Comunes

1. **Error de conexión a Supabase**
   - Verificar variables de entorno
   - Comprobar conectividad de red
   - Validar credenciales de Supabase

2. **Formato de teléfono incorrecto**
   - Asegurar que comience con "573"
   - Verificar que tenga 12 dígitos
   - Limpiar caracteres especiales

3. **Usuario no encontrado**
   - Verificar que existe en la tabla `user_agent`
   - Confirmar que `type = "Administrador"`
   - Validar que el teléfono coincida exactamente

### Debug
```python
# Habilitar logs detallados
import logging
logging.basicConfig(level=logging.DEBUG)
```
