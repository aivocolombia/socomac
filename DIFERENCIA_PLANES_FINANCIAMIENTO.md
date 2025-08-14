# Diferencia entre Planes de Financiamiento

## 🎯 Resumen

**Ambas funciones crean un plan de financiamiento**, pero la diferencia está en el `type_payment_plan` y si se crea un registro adicional en la tabla `letras`.

## 📋 Comparación de Funciones

### 1. `crear_plan_financiamiento()`

**Propósito**: Crear un plan de financiamiento estándar (no letras)

**Parámetros**:
```python
def crear_plan_financiamiento(
    id_sales_orders: int,
    num_installments: int,
    total_amount: float,
    start_date: str,
    frequency: str,
    notes: str = None,
    type_payment_plan: str = "Otro plan de financiamiento"  # Por defecto
) -> str:
```

**Lo que hace**:
1. ✅ Crea un registro en `payment_plan` con `type_payment_plan = "Otro plan de financiamiento"`
2. ✅ Crea las cuotas en `payment_installment`
3. ❌ **NO** crea registro en tabla `letras`

### 2. `crear_plan_letras()`

**Propósito**: Crear un plan de financiamiento tipo "letras"

**Parámetros**:
```python
def crear_plan_letras(
    id_sales_orders: int,
    num_installments: int,
    total_amount: float,
    start_date: str,
    frequency: str,
    letra_number: int,        # OBLIGATORIO para letras
    last_date: str,           # OBLIGATORIO para letras
    notes: str = None
) -> str:
```

**Lo que hace**:
1. ✅ Crea un registro en `payment_plan` con `type_payment_plan = "Letras"`
2. ✅ Crea las cuotas en `payment_installment`
3. ✅ **ADICIONALMENTE** crea un registro en tabla `letras`

## 🔧 Estructura de Base de Datos

### Tabla `payment_plan` (ambas funciones)
```sql
INSERT INTO payment_plan (
    id_sales_orders,
    num_installments,
    total_amount,
    start_date,
    frequency,
    notes,
    pending_amount,
    type_payment_plan,  -- ← DIFERENCIA CLAVE
    status
)
VALUES (
    %s, %s, %s, %s, %s, %s, %s, %s, 'Pendiente'
)
```

**Diferencias en `type_payment_plan`**:
- `crear_plan_financiamiento()` → `"Otro plan de financiamiento"`
- `crear_plan_letras()` → `"Letras"`

### Tabla `letras` (solo `crear_plan_letras()`)
```sql
INSERT INTO letras (
    id_payment_plan,
    letra_number,
    last_date,
    status
)
VALUES (
    %s, %s, %s, 'Pendiente'
)
```

**Donde**:
- `id_payment_plan`: ID del plan creado
- `letra_number`: Número de letra (proporcionado por usuario)
- `last_date`: Última fecha de pago (proporcionada por usuario)
- `status`: 'Pendiente'

## 📱 Flujo de Usuario

### Cuando el usuario elige "Otro plan de financiamiento":
```
Usuario: "Crear plan de financiamiento"
Agente: Solicitar datos básicos (cuotas, monto, fecha, frecuencia)
Usuario: "Tipo: Otro plan de financiamiento"
Agente: Llamar crear_plan_financiamiento()
Resultado: Plan creado con type_payment_plan = "Otro plan de financiamiento"
```

### Cuando el usuario elige "Letras":
```
Usuario: "Crear plan de financiamiento"
Agente: Solicitar datos básicos (cuotas, monto, fecha, frecuencia)
Usuario: "Tipo: Letras"
Agente: Solicitar datos específicos de letras:
  - "¿Cuál es el número de la letra?"
  - "¿Cuál es la última fecha de pago de la letra?"
Usuario: Proporcionar letra_number y last_date
Agente: Llamar crear_plan_letras()
Resultado: 
  - Plan creado con type_payment_plan = "Letras"
  - Registro adicional creado en tabla letras
```

## 🎯 Puntos Clave

### Similitudes:
- ✅ Ambas crean un plan de financiamiento completo
- ✅ Ambas crean las cuotas automáticamente
- ✅ Ambas validan los datos de entrada
- ✅ Ambas muestran confirmación detallada

### Diferencias:
1. **`type_payment_plan`**:
   - `crear_plan_financiamiento()` → `"Otro plan de financiamiento"`
   - `crear_plan_letras()` → `"Letras"`

2. **Datos adicionales**:
   - `crear_plan_financiamiento()` → Solo datos estándar
   - `crear_plan_letras()` → Requiere `letra_number` y `last_date`

3. **Tabla adicional**:
   - `crear_plan_financiamiento()` → Solo `payment_plan` y `payment_installment`
   - `crear_plan_letras()` → `payment_plan`, `payment_installment` + `letras`

## 📝 Ejemplos de Uso

### Ejemplo 1: Otro Plan de Financiamiento
```python
# Usuario elige "Otro plan de financiamiento"
resultado = crear_plan_financiamiento(
    id_sales_orders=123,
    num_installments=12,
    total_amount=5000000,
    start_date="2024-01-15",
    frequency="Mensual",
    notes="Plan estándar"
)
# type_payment_plan = "Otro plan de financiamiento"
# NO se crea registro en tabla letras
```

### Ejemplo 2: Letras
```python
# Usuario elige "Letras"
resultado = crear_plan_letras(
    id_sales_orders=123,
    num_installments=6,
    total_amount=3000000,
    start_date="2024-01-15",
    frequency="Mensual",
    letra_number=5,           # Específico para letras
    last_date="2024-07-15",   # Específico para letras
    notes="Plan de letras"
)
# type_payment_plan = "Letras"
# SÍ se crea registro en tabla letras
```

## ✅ Verificación

Para verificar que funciona correctamente:

1. **Otro plan de financiamiento**:
   ```sql
   SELECT type_payment_plan FROM payment_plan WHERE id_payment_plan = [ID];
   -- Debe retornar: "Otro plan de financiamiento"
   ```

2. **Letras**:
   ```sql
   SELECT type_payment_plan FROM payment_plan WHERE id_payment_plan = [ID];
   -- Debe retornar: "Letras"
   
   SELECT * FROM letras WHERE id_payment_plan = [ID];
   -- Debe retornar un registro con letra_number y last_date
   ```

## 🎯 Conclusión

La diferencia principal es que **ambas crean planes de financiamiento**, pero:
- **"Otro plan de financiamiento"** → Solo crea el plan estándar
- **"Letras"** → Crea el plan + registro adicional en tabla `letras` con datos específicos de letra
