# 🤖 HERRAMIENTAS PARA AGENTE DE IA - SISTEMA DE CUOTAS Y ABONOS

## 📋 **DESCRIPCIÓN GENERAL**

Este documento contiene las herramientas y prompts necesarios para implementar un agente de IA que maneje la funcionalidad de **Pago de Cuotas o Abonos** del sistema SOCOMAC Truck POS. El agente debe replicar exactamente la funcionalidad del botón "Pago de Cuota o Abono" presente en la página de Conciliaciones.

---

## 🎯 **FUNCIONALIDAD A REPLICAR**

### **Botón: "Pago de Cuota o Abono"**
- **Ubicación**: Página de Conciliaciones
- **Acción**: Abre modal para registrar pagos de cuotas pendientes
- **Requisito**: Solo funciona cuando la caja está abierta

---

## 🛠️ **HERRAMIENTAS DEL AGENTE**

### **1. HERRAMIENTA: `registrar_pago_cuota`**

```json
{
  "name": "registrar_pago_cuota",
  "description": "Registra un pago de cuota o abono para un cliente específico en el sistema SOCOMAC",
  "parameters": {
    "type": "object",
    "properties": {
      "cliente_id": {
        "type": "integer",
        "description": "ID del cliente que realiza el pago"
      },
      "plan_financiamiento_id": {
        "type": "integer", 
        "description": "ID del plan de financiamiento al que pertenece la cuota"
      },
      "cuotas_seleccionadas": {
        "type": "array",
        "items": {"type": "integer"},
        "description": "Array con los números de cuotas a pagar (ej: [1, 2, 3])"
      },
      "valor_pagar": {
        "type": "number",
        "description": "Valor total a pagar en pesos colombianos"
      },
      "metodo_pago": {
        "type": "string",
        "enum": ["efectivo", "transferencia", "cheque"],
        "description": "Método de pago utilizado"
      },
      "datos_adicionales": {
        "type": "object",
        "description": "Datos adicionales según el método de pago",
        "properties": {
          "numero_comprobante": {"type": "string"},
          "banco_emision": {"type": "string"},
          "fecha_emision": {"type": "string", "format": "date"},
          "banco_destino": {"type": "string"},
          "numero_cheque": {"type": "string"},
          "fecha_estimada_cobro": {"type": "string", "format": "date"},
          "banco_emision_cheque": {"type": "string"},
          "fecha_emision_cheque": {"type": "string", "format": "date"},
          "comentarios": {"type": "string"}
        }
      }
    },
    "required": ["cliente_id", "plan_financiamiento_id", "cuotas_seleccionadas", "valor_pagar", "metodo_pago"]
  }
}
```

### **2. HERRAMIENTA: `consultar_cuotas_pendientes`**

```json
{
  "name": "consultar_cuotas_pendientes",
  "description": "Consulta las cuotas pendientes de pago para un cliente específico",
  "parameters": {
    "type": "object",
    "properties": {
      "cliente_id": {
        "type": "integer",
        "description": "ID del cliente para consultar sus cuotas"
      },
      "plan_financiamiento_id": {
        "type": "integer",
        "description": "ID específico del plan (opcional, si no se proporciona retorna todos los planes del cliente)"
      }
    },
    "required": ["cliente_id"]
  }
}
```

### **3. HERRAMIENTA: `consultar_estado_caja`**

```json
{
  "name": "consultar_estado_caja",
  "description": "Verifica si la caja está abierta para permitir transacciones",
  "parameters": {
    "type": "object",
    "properties": {},
    "required": []
  }
}
```

### **4. HERRAMIENTA: `consultar_clientes`**

```json
{
  "name": "consultar_clientes",
  "description": "Consulta la lista de clientes disponibles en el sistema",
  "parameters": {
    "type": "object",
    "properties": {
      "filtro": {
        "type": "string",
        "description": "Filtro opcional para buscar clientes por nombre o identificación"
      }
    },
    "required": []
  }
}
```

---

## 🧠 **PROMPT PRINCIPAL DEL AGENTE**

```
Eres un asistente especializado en el sistema SOCOMAC Truck POS para el manejo de pagos de cuotas y abonos. Tu función principal es ayudar a los usuarios a registrar pagos de cuotas pendientes de manera eficiente y precisa.

## CONTEXTO DEL SISTEMA:
- SOCOMAC es una empresa de repuestos para vehículos pesados
- El sistema maneja planes de financiamiento con cuotas mensuales
- Los pagos pueden ser en efectivo, transferencia o cheque
- Solo se pueden registrar pagos cuando la caja está abierta

## FUNCIONALIDADES PRINCIPALES:

### 1. REGISTRO DE PAGOS DE CUOTAS
- Verificar que la caja esté abierta antes de procesar cualquier pago
- Consultar cuotas pendientes del cliente
- Validar que el valor a pagar sea correcto
- Registrar el pago en la base de datos
- Actualizar el estado de las cuotas (pagada/parcialmente pagada)
- Actualizar el plan de financiamiento si todas las cuotas están pagadas

### 2. VALIDACIONES CRÍTICAS:
- La caja debe estar abierta
- El cliente debe existir en el sistema
- El plan de financiamiento debe estar activo
- Las cuotas seleccionadas deben estar pendientes
- El valor a pagar debe ser válido
- Los datos del método de pago deben ser completos según el tipo

### 3. FLUJO DE TRABAJO:
1. Verificar estado de caja
2. Identificar cliente (por nombre o ID)
3. Consultar cuotas pendientes
4. Validar datos del pago
5. Registrar pago en base de datos
6. Actualizar estados de cuotas
7. Confirmar operación exitosa

## INSTRUCCIONES ESPECÍFICAS:

### AL RECIBIR UNA SOLICITUD DE PAGO:
1. SIEMPRE verificar primero el estado de la caja
2. Si la caja está cerrada, informar al usuario que debe abrirla primero
3. Buscar al cliente por nombre o identificación
4. Mostrar las cuotas pendientes disponibles
5. Validar todos los datos antes de proceder
6. Confirmar la operación antes de ejecutarla

### AL MANEJAR ERRORES:
- Proporcionar mensajes claros y específicos
- Sugerir soluciones cuando sea posible
- Mantener un tono profesional y útil

### AL CONFIRMAR OPERACIONES:
- Mostrar resumen de la operación
- Confirmar datos importantes (cliente, monto, cuotas)
- Proporcionar número de referencia si está disponible

## FORMATO DE RESPUESTAS:
- Usar emojis para hacer las respuestas más amigables
- Estructurar la información de manera clara
- Incluir confirmaciones visuales cuando sea apropiado
- Proporcionar detalles técnicos cuando sea necesario

Recuerda: Tu objetivo es hacer que el proceso de pago de cuotas sea simple, seguro y eficiente para los usuarios del sistema SOCOMAC.
```

---

## 📊 **ESTRUCTURA DE DATOS**

### **Tablas Principales Involucradas:**

#### **1. `clients` - Información de Clientes**
```sql
- id_client: integer (PK)
- full_name: string
- first_name: string  
- last_name: string
- unique_id: string (identificación)
- client_type: string
- company: string
- phone: string
- email: string
```

#### **2. `payment_plan` - Planes de Financiamiento**
```sql
- id_payment_plan: integer (PK)
- id_sales_orders: integer (FK)
- num_installments: integer
- total_amount: decimal
- start_date: date
- frequency: string
- id_status: integer
- type_payment_plan: string
```

#### **3. `payment_installment` - Cuotas Individuales**
```sql
- id_payment_installment: integer (PK)
- id_payment_plan: integer (FK)
- installment_number: integer
- amount: decimal (valor de la cuota)
- pay_amount: decimal (monto pagado)
- due_date: date
- id_status: integer
- payment_date: date
```

#### **4. `payments` - Registro de Pagos**
```sql
- id_payment: integer (PK)
- id_client: integer (FK)
- id_payment_installment: integer (FK)
- amount: decimal
- payment_date: date
- id_destiny_bank: integer
- notes: string
- type: string
```

#### **5. `status_caja` - Estado de Caja**
```sql
- id: integer (PK)
- status: boolean (true = abierta, false = cerrada)
- amount: decimal
- created_at: timestamp
```

---

## 🔄 **FLUJO DE PROCESAMIENTO**

### **Paso 1: Validación de Caja**
```javascript
// Verificar que la caja esté abierta
const estadoCaja = await consultar_estado_caja();
if (!estadoCaja.status) {
  return "❌ La caja está cerrada. Debe abrir la caja antes de registrar pagos.";
}
```

### **Paso 2: Identificación del Cliente**
```javascript
// Buscar cliente por nombre o identificación
const clientes = await consultar_clientes({ filtro: "Juan Pérez" });
if (clientes.length === 0) {
  return "❌ Cliente no encontrado. Verifique el nombre o identificación.";
}
```

### **Paso 3: Consulta de Cuotas Pendientes**
```javascript
// Obtener cuotas pendientes del cliente
const cuotasPendientes = await consultar_cuotas_pendientes({
  cliente_id: cliente.id_client
});
```

### **Paso 4: Validación de Datos**
```javascript
// Validar que las cuotas seleccionadas estén pendientes
// Validar que el valor a pagar sea correcto
// Validar datos del método de pago
```

### **Paso 5: Registro del Pago**
```javascript
// Registrar el pago en la base de datos
const resultado = await registrar_pago_cuota({
  cliente_id: cliente.id_client,
  plan_financiamiento_id: plan.id_payment_plan,
  cuotas_seleccionadas: [1, 2],
  valor_pagar: 500000,
  metodo_pago: "efectivo",
  datos_adicionales: {
    comentarios: "Pago de cuotas 1 y 2"
  }
});
```

---

## ⚠️ **VALIDACIONES CRÍTICAS**

### **1. Estado de Caja**
- ✅ Caja debe estar abierta
- ❌ No se pueden registrar pagos con caja cerrada

### **2. Cliente**
- ✅ Cliente debe existir en el sistema
- ✅ Debe tener planes de financiamiento activos

### **3. Plan de Financiamiento**
- ✅ Plan debe estar activo (id_status != 10)
- ✅ Debe tener cuotas pendientes

### **4. Cuotas**
- ✅ Cuotas seleccionadas deben existir
- ✅ Cuotas deben estar pendientes (id_status != 6)
- ✅ Valor a pagar debe ser válido

### **5. Método de Pago**
- ✅ Efectivo: Solo requiere comentarios
- ✅ Transferencia: Requiere número de comprobante, banco emisión, fecha emisión, banco destino
- ✅ Cheque: Requiere número de cheque, fecha estimada de cobro, banco emisión, fecha emisión

---

## 🎯 **CASOS DE USO COMUNES**

### **Caso 1: Pago de Cuota en Efectivo**
```
Usuario: "Quiero registrar un pago de $300,000 en efectivo para Juan Pérez, cuota número 2"

Agente:
1. Verifica estado de caja ✅
2. Busca cliente "Juan Pérez" ✅
3. Consulta cuotas pendientes ✅
4. Valida cuota número 2 ✅
5. Registra pago ✅
6. Confirma operación ✅
```

### **Caso 2: Pago Múltiple con Transferencia**
```
Usuario: "María García quiere pagar las cuotas 1, 2 y 3 por transferencia, $900,000 total"

Agente:
1. Verifica estado de caja ✅
2. Busca cliente "María García" ✅
3. Consulta cuotas pendientes ✅
4. Valida cuotas 1, 2, 3 ✅
5. Solicita datos de transferencia
6. Registra pago ✅
7. Confirma operación ✅
```

### **Caso 3: Caja Cerrada**
```
Usuario: "Quiero pagar una cuota"

Agente:
1. Verifica estado de caja ❌
2. Informa: "❌ La caja está cerrada. Debe abrir la caja antes de registrar pagos."
```

---

## 📝 **MENSAJES DE RESPUESTA ESTÁNDAR**

### **Éxito:**
```
✅ Pago registrado exitosamente
📊 Cliente: Juan Pérez
💰 Monto: $300,000
📅 Cuotas pagadas: 2
💳 Método: Efectivo
🆔 Referencia: PAY-2025-001
```

### **Error - Caja Cerrada:**
```
❌ No se puede procesar el pago
🔒 La caja está cerrada
💡 Debe abrir la caja antes de registrar pagos
```

### **Error - Cliente No Encontrado:**
```
❌ Cliente no encontrado
🔍 Verifique el nombre o identificación
💡 Clientes disponibles: [lista de clientes]
```

### **Error - Cuotas No Válidas:**
```
❌ Cuotas no válidas
📋 Cuotas pendientes disponibles: [lista de cuotas]
💡 Verifique los números de cuota seleccionados
```

---

## 🔧 **CONFIGURACIÓN TÉCNICA**

### **Base de Datos:**
- **Sistema**: Supabase (PostgreSQL)
- **Autenticación**: RLS (Row Level Security)
- **Conexión**: Via cliente Supabase

### **Endpoints Principales:**
- `GET /status_caja` - Estado de caja
- `GET /clients` - Lista de clientes
- `GET /payment_plan` - Planes de financiamiento
- `GET /payment_installment` - Cuotas
- `POST /payments` - Registrar pago
- `PUT /payment_installment` - Actualizar cuota
- `PUT /payment_plan` - Actualizar plan

### **Estados de Cuotas:**
- `1` - Pendiente
- `6` - Pagada
- `8` - Pago Parcial
- `9` - Vencida

### **Estados de Planes:**
- `1` - Activo
- `10` - Finalizado

---

## 🚀 **IMPLEMENTACIÓN**

Para implementar este agente:

1. **Configurar conexión a Supabase** con las credenciales del proyecto
2. **Implementar las 4 herramientas** descritas anteriormente
3. **Configurar el prompt principal** en el sistema de IA
4. **Probar con casos de uso** comunes
5. **Validar integridad** de datos en la base de datos

---

## 📞 **SOPORTE**

Para dudas sobre la implementación o funcionamiento del sistema, consultar:
- Documentación técnica del proyecto SOCOMAC
- Esquema de base de datos en `SUPABASE_SCHEMA.md`
- Código fuente en `src/pages/Conciliaciones.tsx`

---

*Documento creado para el proyecto SOCOMAC Truck POS - Sistema de Gestión de Repuestos*
