# Esquema de Base de Datos Anterior - SOCOMAC

Este documento contiene el esquema anterior de la base de datos del sistema SOCOMAC para referencia y comparación con el esquema actual.

## ⚠️ ADVERTENCIA
Este esquema es solo para contexto y no está diseñado para ser ejecutado directamente. El orden de las tablas y las restricciones pueden no ser válidos para la ejecución.

---

## Tablas del Sistema Anterior

### 1. **category** - Categorías de Productos
```sql
CREATE TABLE public.category (
  created_by_user integer,
  created_at timestamp without time zone DEFAULT now(),
  updated_at timestamp without time zone DEFAULT now(),
  id_category integer NOT NULL DEFAULT nextval('brands_id_brand_seq'::regclass),
  name_category character varying,
  CONSTRAINT category_pkey PRIMARY KEY (id_category),
  CONSTRAINT brands_created_by_user_fkey FOREIGN KEY (created_by_user) REFERENCES public.users(id_user)
);
```
**Comentarios:**
- Categorías para clasificar productos
- Incluye campo `created_by_user` para auditoría
- **Nota**: Usa secuencia `brands_id_brand_seq` (posible error de nomenclatura)

### 2. **cheques** - Cheques
```sql
CREATE TABLE public.cheques (
  last_date date,
  emision_date date NOT NULL,
  cheque_value numeric NOT NULL,
  id_payment integer,
  cheque_number character varying NOT NULL,
  bank character varying,
  stimate_collection_date date,
  real_collection_date date,
  days_overdue integer,
  collection_method text,
  observations text,
  status character varying DEFAULT 'Pendiente'::character varying,
  id_cheque integer NOT NULL DEFAULT nextval('cheques_id_chque_seq'::regclass),
  created_by_user integer,
  created_at timestamp without time zone DEFAULT now(),
  updated_at timestamp without time zone DEFAULT now(),
  id_payment_plan integer,
  CONSTRAINT cheques_pkey PRIMARY KEY (id_cheque),
  CONSTRAINT fk_payment FOREIGN KEY (id_payment) REFERENCES public.payments(id_payment),
  CONSTRAINT cheques_id_payment_plan_fkey FOREIGN KEY (id_payment_plan) REFERENCES public.payment_plan(id_payment_plan),
  CONSTRAINT fk_created_by_user FOREIGN KEY (created_by_user) REFERENCES public.users(id_user)
);
```
**Comentarios:**
- Maneja información completa de cheques
- Incluye campos adicionales: `days_overdue`, `collection_method`, `last_date`
- Status por defecto: 'Pendiente'
- **Nota**: Secuencia con typo `cheques_id_chque_seq` (falta 'e')

### 3. **classification** - Clasificaciones
```sql
CREATE TABLE public.classification (
  nombre character varying,
  primer_apellido character varying,
  segundo_apellido character varying,
  description text,
  ejemplos character varying,
  created_by_user integer,
  id_classification integer NOT NULL DEFAULT nextval('classification_id_classification_seq'::regclass),
  created_at timestamp without time zone DEFAULT now(),
  updated_at timestamp without time zone DEFAULT now(),
  type text,
  comments text,
  CONSTRAINT classification_pkey PRIMARY KEY (id_classification),
  CONSTRAINT classification_created_by_user_fkey FOREIGN KEY (created_by_user) REFERENCES public.users(id_user)
);
```
**Comentarios:**
- Clasificaciones para órdenes de venta
- Incluye campos de nombres personales (posiblemente para personas de contacto)
- Campo `ejemplos` en lugar de `examples`

### 4. **clients** - Clientes
```sql
CREATE TABLE public.clients (
  client_type character varying,
  unique_id character varying,
  created_by_user integer,
  id_client integer NOT NULL DEFAULT nextval('clients_id_client_seq'::regclass),
  created_at timestamp without time zone DEFAULT now(),
  updated_at timestamp without time zone DEFAULT now(),
  last_name text,
  full_name text,
  deparment text,
  city text,
  address text,
  company text,
  first_name text,
  email text,
  phone text,
  client_classification character varying,
  phone_2 text,
  CONSTRAINT clients_pkey PRIMARY KEY (id_client),
  CONSTRAINT clients_created_by_user_fkey FOREIGN KEY (created_by_user) REFERENCES public.users(id_user)
);
```
**Comentarios:**
- Información completa de clientes
- **Nota**: Typo en `deparment` (debería ser `department`)
- Campos de texto en lugar de `character varying`
- Incluye auditoría con `created_by_user`

### 5. **estado_caja** - Estado de Caja
```sql
CREATE TABLE public.estado_caja (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  estado_caj boolean,
  created_at timestamp with time zone NOT NULL DEFAULT now(),
  saldo_inicial numeric,
  updated_at timestamp with time zone,
  identificador text,
  CONSTRAINT estado_caja_pkey PRIMARY KEY (id)
);
```
**Comentarios:**
- **TABLA CRÍTICA**: Controla el estado de caja
- **Diferencias con esquema actual:**
  - Campo `estado_caj` (posible typo, debería ser `estado_caja`)
  - Campo `identificador` para identificar tipo de caja
  - Estructura más simple que `status_caja` actual

### 6. **expenses** - Gastos
```sql
CREATE TABLE public.expenses (
  caja_receipt text,
  id_classification integer,
  paid_to character varying,
  amount numeric,
  payment_method character varying,
  notes text,
  created_by_user integer,
  id_expense integer NOT NULL DEFAULT nextval('expenses_id_expense_seq'::regclass),
  created_at timestamp without time zone DEFAULT now(),
  updated_at timestamp without time zone DEFAULT now(),
  payment_date date,
  payment_bank text,
  segundo_apellido text,
  CONSTRAINT expenses_pkey PRIMARY KEY (id_expense),
  CONSTRAINT expenses_id_classification_fkey FOREIGN KEY (id_classification) REFERENCES public.classification(id_classification),
  CONSTRAINT expenses_created_by_user_fkey FOREIGN KEY (created_by_user) REFERENCES public.users(id_user)
);
```
**Comentarios:**
- **TABLA NUEVA**: No existe en el esquema actual
- Maneja gastos del negocio
- Incluye campo `segundo_apellido` (posiblemente para persona que recibe el pago)
- Relacionada con clasificaciones

### 7. **interactions** - Interacciones
```sql
CREATE TABLE public.interactions (
  caja boolean,
  user_admin numeric,
  id integer NOT NULL DEFAULT nextval('interactions_id_seq'::regclass),
  CONSTRAINT interactions_pkey PRIMARY KEY (id)
);
```
**Comentarios:**
- **TABLA NUEVA**: No existe en el esquema actual
- Parece ser para tracking de interacciones del sistema
- Campos muy básicos: `caja` y `user_admin`

### 8. **inventory** - Inventario
```sql
CREATE TABLE public.inventory (
  id_product integer,
  movement_date date,
  movement_type character varying,
  quantity integer,
  notes text,
  created_by_user integer,
  id_inventory_movement integer NOT NULL DEFAULT nextval('inventory_id_inventory_movement_seq'::regclass),
  created_at timestamp without time zone DEFAULT now(),
  updated_at timestamp without time zone DEFAULT now(),
  CONSTRAINT inventory_pkey PRIMARY KEY (id_inventory_movement),
  CONSTRAINT inventory_created_by_user_fkey FOREIGN KEY (created_by_user) REFERENCES public.users(id_user),
  CONSTRAINT inventory_id_product_fkey FOREIGN KEY (id_product) REFERENCES public.products(id_product)
);
```
**Comentarios:**
- Movimientos de inventario
- **Diferencias con esquema actual:**
  - `movement_type` como `character varying` en lugar de referencia a tabla
  - Incluye auditoría con `created_by_user`

### 9. **letras** - Letras
```sql
CREATE TABLE public.letras (
  last_date date,
  days_overdue numeric,
  status text,
  id_payment_plan integer,
  letra_number numeric,
  created_by_user integer,
  id_letras integer NOT NULL DEFAULT nextval('letras_id_letras_seq'::regclass),
  created_at timestamp without time zone DEFAULT now(),
  updated_at timestamp without time zone DEFAULT now(),
  CONSTRAINT letras_pkey PRIMARY KEY (id_letras),
  CONSTRAINT letras_created_by_user_fkey FOREIGN KEY (created_by_user) REFERENCES public.users(id_user),
  CONSTRAINT letras_id_payment_plan_fkey FOREIGN KEY (id_payment_plan) REFERENCES public.payment_plan(id_payment_plan)
);
```
**Comentarios:**
- Letras de cambio para planes de financiamiento
- **Diferencias con esquema actual:**
  - Campos adicionales: `last_date`, `days_overdue`
  - `letra_number` como `numeric` en lugar de `character varying`
  - Incluye auditoría

### 10. **payment_installment** - Cuotas de Pago
```sql
CREATE TABLE public.payment_installment (
  id_payment_plan integer,
  installment_number integer,
  due_date date,
  amount numeric,
  status character varying,
  payment_date date,
  created_by_user integer,
  id_payment_installment integer NOT NULL DEFAULT nextval('payment_installment_id_payment_installment_seq'::regclass),
  created_at timestamp without time zone DEFAULT now(),
  pay_amount numeric DEFAULT NULL::numeric,
  updated_at timestamp without time zone DEFAULT now(),
  early_payment_discount numeric,
  daysoverdue bigint,
  CONSTRAINT payment_installment_pkey PRIMARY KEY (id_payment_installment),
  CONSTRAINT payment_installment_id_payment_plan_fkey FOREIGN KEY (id_payment_plan) REFERENCES public.payment_plan(id_payment_plan),
  CONSTRAINT payment_installment_created_by_user_fkey FOREIGN KEY (created_by_user) REFERENCES public.users(id_user)
);
```
**Comentarios:**
- Cuotas individuales de los planes de financiamiento
- **Diferencias con esquema actual:**
  - `status` como `character varying` en lugar de referencia a tabla
  - Campo adicional: `daysoverdue` (sin separación)
  - Incluye auditoría

### 11. **payment_plan** - Planes de Pago
```sql
CREATE TABLE public.payment_plan (
  id_sales_orders integer,
  num_installments integer,
  total_amount numeric,
  start_date date,
  status character varying,
  notes text,
  created_by_user integer,
  frequency text,
  id_payment_plan integer NOT NULL DEFAULT nextval('payment_plan_id_payment_plan_seq'::regclass),
  created_at timestamp without time zone DEFAULT now(),
  updated_at timestamp without time zone DEFAULT now(),
  pending_amount numeric,
  type_payment_plan text,
  CONSTRAINT payment_plan_pkey PRIMARY KEY (id_payment_plan),
  CONSTRAINT payment_plan_id_sales_orders_fkey FOREIGN KEY (id_sales_orders) REFERENCES public.sales_orders(id_sales_orders),
  CONSTRAINT payment_plan_created_by_user_fkey FOREIGN KEY (created_by_user) REFERENCES public.users(id_user)
);
```
**Comentarios:**
- Planes de financiamiento para órdenes de venta
- **Diferencias con esquema actual:**
  - `status` como `character varying` en lugar de referencia a tabla
  - Campo adicional: `pending_amount`
  - Incluye auditoría

### 12. **payments** - Pagos
```sql
CREATE TABLE public.payments (
  caja_receipt text,
  id_client integer,
  id_classification integer,
  id_sales_orders integer,
  id_payment_installment integer,
  payment_method character varying,
  amount numeric,
  payment_date date,
  notes text,
  created_by_user integer,
  destiny_bank text,
  id_payment integer NOT NULL DEFAULT nextval('payments_id_payment_seq'::regclass),
  created_at timestamp without time zone DEFAULT now(),
  updated_at timestamp without time zone DEFAULT now(),
  type character varying CHECK (type::text = ANY (ARRAY['payment'::character varying, 'credit'::character varying, 'refund'::character varying, 'adjustment'::character varying]::text[])),
  origin_return_id bigint,
  segundo_apellido text,
  CONSTRAINT payments_pkey PRIMARY KEY (id_payment),
  CONSTRAINT payments_created_by_user_fkey FOREIGN KEY (created_by_user) REFERENCES public.users(id_user),
  CONSTRAINT fk_id_client FOREIGN KEY (id_client) REFERENCES public.clients(id_client),
  CONSTRAINT payments_origin_return_id_fkey FOREIGN KEY (origin_return_id) REFERENCES public.returns_log(id_return),
  CONSTRAINT payments_id_sales_orders_fkey FOREIGN KEY (id_sales_orders) REFERENCES public.sales_orders(id_sales_orders),
  CONSTRAINT payments_id_payment_installment_fkey FOREIGN KEY (id_payment_installment) REFERENCES public.payment_installment(id_payment_installment),
  CONSTRAINT fk_id_classification FOREIGN KEY (id_classification) REFERENCES public.classification(id_classification)
);
```
**Comentarios:**
- Tabla central de pagos del sistema
- **Diferencias con esquema actual:**
  - `destiny_bank` como `text` en lugar de referencia a tabla `banks`
  - Campo adicional: `segundo_apellido`
  - Constraint CHECK para tipos de pago
  - Incluye auditoría

### 13. **products** - Productos
```sql
CREATE TABLE public.products (
  description text,
  condition character varying,
  unit_price numeric,
  created_by_user integer,
  name_product character varying,
  id_product integer NOT NULL DEFAULT nextval('products_id_product_seq'::regclass),
  created_at timestamp without time zone DEFAULT now(),
  updated_at timestamp without time zone DEFAULT now(),
  id_category bigint,
  factory_reference text,
  taxes text,
  CONSTRAINT products_pkey PRIMARY KEY (id_product),
  CONSTRAINT products_created_by_user_fkey FOREIGN KEY (created_by_user) REFERENCES public.users(id_user),
  CONSTRAINT id_category FOREIGN KEY (id_category) REFERENCES public.category(id_category)
);
```
**Comentarios:**
- Catálogo de productos del sistema
- **Diferencias con esquema actual:**
  - `condition` como `character varying` en lugar de referencia a tabla
  - Incluye auditoría
  - Constraint con nombre genérico `id_category`

### 14. **purchase_order_details** - Detalles de Órdenes de Compra
```sql
CREATE TABLE public.purchase_order_details (
  id_purchase_order integer,
  id_product integer,
  quantity integer,
  unit_price numeric,
  subtotal numeric,
  created_by_user integer,
  id_purchase_order_detail integer NOT NULL DEFAULT nextval('purchase_order_details_id_purchase_order_detail_seq'::regclass),
  created_at timestamp without time zone DEFAULT now(),
  updated_at timestamp without time zone DEFAULT now(),
  CONSTRAINT purchase_order_details_pkey PRIMARY KEY (id_purchase_order_detail),
  CONSTRAINT purchase_order_details_created_by_user_fkey FOREIGN KEY (created_by_user) REFERENCES public.users(id_user),
  CONSTRAINT purchase_order_details_id_product_fkey FOREIGN KEY (id_product) REFERENCES public.products(id_product),
  CONSTRAINT purchase_order_details_id_purchase_order_fkey FOREIGN KEY (id_purchase_order) REFERENCES public.purchase_orders(id_purchase_order)
);
```
**Comentarios:**
- Detalles de productos en órdenes de compra
- Incluye auditoría con `created_by_user`

### 15. **purchase_orders** - Órdenes de Compra
```sql
CREATE TABLE public.purchase_orders (
  id_supplier integer,
  order_date date,
  status character varying,
  total numeric,
  notes text,
  created_by_user integer,
  id_purchase_order integer NOT NULL DEFAULT nextval('purchase_orders_id_purchase_order_seq'::regclass),
  created_at timestamp without time zone DEFAULT now(),
  updated_at timestamp without time zone DEFAULT now(),
  CONSTRAINT purchase_orders_pkey PRIMARY KEY (id_purchase_order),
  CONSTRAINT purchase_orders_created_by_user_fkey FOREIGN KEY (created_by_user) REFERENCES public.users(id_user),
  CONSTRAINT purchase_orders_id_supplier_fkey FOREIGN KEY (id_supplier) REFERENCES public.suppliers(id_supplier)
);
```
**Comentarios:**
- Órdenes de compra a proveedores
- **Diferencias con esquema actual:**
  - Estructura más simple (sin campos bancarios ni clasificación)
  - `status` como `character varying` en lugar de referencia a tabla
  - Incluye auditoría

### 16. **returns_log** - Log de Devoluciones
```sql
CREATE TABLE public.returns_log (
  id_sales_orders bigint NOT NULL,
  id_sales_order_detail bigint NOT NULL,
  id_client bigint NOT NULL,
  amount numeric NOT NULL CHECK (amount > 0::numeric),
  action_type character varying NOT NULL CHECK (action_type::text = ANY (ARRAY['refund'::character varying, 'credit'::character varying]::text[])),
  target_order_id bigint,
  target_quota_id bigint,
  notes text,
  created_by character varying,
  id_return bigint NOT NULL DEFAULT nextval('returns_log_id_return_seq'::regclass),
  status character varying NOT NULL DEFAULT 'pending'::character varying CHECK (status::text = ANY (ARRAY['pending'::character varying, 'processed'::character varying]::text[])),
  created_at timestamp with time zone DEFAULT now(),
  quantity numeric CHECK (quantity > 0::numeric),
  processed_amount numeric,
  CONSTRAINT returns_log_pkey PRIMARY KEY (id_return),
  CONSTRAINT returns_log_target_quota_id_fkey FOREIGN KEY (target_quota_id) REFERENCES public.payment_installment(id_payment_installment),
  CONSTRAINT returns_log_target_order_id_fkey FOREIGN KEY (target_order_id) REFERENCES public.sales_orders(id_sales_orders),
  CONSTRAINT returns_log_id_sales_orders_fkey FOREIGN KEY (id_sales_orders) REFERENCES public.sales_orders(id_sales_orders),
  CONSTRAINT returns_log_id_client_fkey FOREIGN KEY (id_client) REFERENCES public.clients(id_client),
  CONSTRAINT returns_log_id_sales_order_detail_fkey FOREIGN KEY (id_sales_order_detail) REFERENCES public.sales_order_details(id_sales_order_detail)
);
```
**Comentarios:**
- Registro de todas las devoluciones del sistema
- **Diferencias con esquema actual:**
  - Campos obligatorios: `id_sales_orders`, `id_sales_order_detail`, `id_client`
  - Constraints CHECK para validaciones
  - `created_by` como `character varying` en lugar de referencia a usuario

### 17. **sales_order_details** - Detalles de Órdenes de Venta
```sql
CREATE TABLE public.sales_order_details (
  devolucion text,
  id_sales_orders integer,
  id_product integer,
  quantity integer,
  created_by_user integer,
  id_sales_order_detail integer NOT NULL DEFAULT nextval('sales_order_details_id_sales_order_detail_seq'::regclass),
  created_at timestamp without time zone DEFAULT now(),
  updated_at timestamp without time zone DEFAULT now(),
  unit_price bigint,
  subtotal bigint,
  CONSTRAINT sales_order_details_pkey PRIMARY KEY (id_sales_order_detail),
  CONSTRAINT sales_order_details_created_by_user_fkey FOREIGN KEY (created_by_user) REFERENCES public.users(id_user),
  CONSTRAINT sales_order_details_id_sales_orders_fkey FOREIGN KEY (id_sales_orders) REFERENCES public.sales_orders(id_sales_orders),
  CONSTRAINT sales_order_details_id_product_fkey FOREIGN KEY (id_product) REFERENCES public.products(id_product)
);
```
**Comentarios:**
- Detalles de productos en órdenes de venta
- **Diferencias con esquema actual:**
  - Incluye auditoría con `created_by_user`
  - Precios en bigint (considerar división por 1000)

### 18. **sales_orders** - Órdenes de Venta
```sql
CREATE TABLE public.sales_orders (
  id_client integer,
  id_classification integer,
  order_date date,
  delivery_date date,
  status character varying,
  total numeric,
  percentage_paid numeric,
  notes text,
  created_by_user integer,
  outstanding_balance numeric DEFAULT '0'::numeric,
  created_at timestamp without time zone DEFAULT now(),
  updated_at timestamp without time zone DEFAULT now(),
  id_sales_orders integer NOT NULL DEFAULT nextval('sales_orders_id_sales_orders_seq'::regclass),
  discount numeric,
  CONSTRAINT sales_orders_pkey PRIMARY KEY (id_sales_orders),
  CONSTRAINT sales_orders_id_client_fkey FOREIGN KEY (id_client) REFERENCES public.clients(id_client),
  CONSTRAINT sales_orders_id_classification_fkey FOREIGN KEY (id_classification) REFERENCES public.classification(id_classification),
  CONSTRAINT sales_orders_created_by_user_fkey FOREIGN KEY (created_by_user) REFERENCES public.users(id_user)
);
```
**Comentarios:**
- Tabla central de órdenes de venta
- **Diferencias con esquema actual:**
  - `status` como `character varying` en lugar de referencia a tabla
  - Incluye auditoría
  - `outstanding_balance` con valor por defecto

### 19. **shipments** - Envíos
```sql
CREATE TABLE public.shipments (
  comments_shipping text,
  id_sales_order integer,
  shipping_address text,
  shipping_city text,
  tracking_number text,
  shipping_method text,
  shipped_date timestamp without time zone,
  estimated_delivery timestamp without time zone,
  delivered_date timestamp without time zone,
  shipping_status text,
  id_shipment integer NOT NULL DEFAULT nextval('shipments_id_shipment_seq'::regclass),
  created_at timestamp without time zone DEFAULT now(),
  CONSTRAINT shipments_pkey PRIMARY KEY (id_shipment),
  CONSTRAINT shipments_id_sales_order_fkey FOREIGN KEY (id_sales_order) REFERENCES public.sales_orders(id_sales_orders)
);
```
**Comentarios:**
- Información de envíos para órdenes de venta
- **Diferencias con esquema actual:**
  - Campos adicionales: `comments_shipping`, `shipping_city`, `shipping_method`
  - Fechas como `timestamp` en lugar de `date`
  - `shipping_status` como `text` en lugar de `character varying`

### 20. **supplier_product** - Productos de Proveedor
```sql
CREATE TABLE public.supplier_product (
  id_supplier integer,
  id_product integer,
  cost_price numeric,
  lead_time_days integer,
  notes text,
  created_by_user integer,
  id_supplier_product integer NOT NULL DEFAULT nextval('supplier_product_id_supplier_product_seq'::regclass),
  created_at timestamp without time zone DEFAULT now(),
  updated_at timestamp without time zone DEFAULT now(),
  CONSTRAINT supplier_product_pkey PRIMARY KEY (id_supplier_product),
  CONSTRAINT supplier_product_id_product_fkey FOREIGN KEY (id_product) REFERENCES public.products(id_product),
  CONSTRAINT supplier_product_id_supplier_fkey FOREIGN KEY (id_supplier) REFERENCES public.suppliers(id_supplier),
  CONSTRAINT supplier_product_created_by_user_fkey FOREIGN KEY (created_by_user) REFERENCES public.users(id_user)
);
```
**Comentarios:**
- Relación entre proveedores y productos
- Incluye auditoría con `created_by_user`

### 21. **suppliers** - Proveedores
```sql
CREATE TABLE public.suppliers (
  company_name character varying,
  contact_name character varying,
  phone character varying,
  email character varying,
  website character varying,
  address character varying,
  notes text,
  created_by_user integer,
  id_supplier integer NOT NULL DEFAULT nextval('suppliers_id_supplier_seq'::regclass),
  created_at timestamp without time zone DEFAULT now(),
  updated_at timestamp without time zone DEFAULT now(),
  CONSTRAINT suppliers_pkey PRIMARY KEY (id_supplier),
  CONSTRAINT suppliers_created_by_user_fkey FOREIGN KEY (created_by_user) REFERENCES public.users(id_user)
);
```
**Comentarios:**
- Información de proveedores del sistema
- Incluye auditoría con `created_by_user`

### 22. **transfers** - Transferencias
```sql
CREATE TABLE public.transfers (
  id_payment integer NOT NULL,
  proof_number character varying NOT NULL,
  emission_bank character varying NOT NULL,
  trans_value numeric NOT NULL,
  emission_date date NOT NULL,
  destiny_bank character varying NOT NULL,
  observations text,
  created_by_user uuid,
  id_transfer integer NOT NULL DEFAULT nextval('transfers_id_transfer_seq'::regclass),
  status character varying DEFAULT 'Pending'::character varying,
  updated_at timestamp with time zone DEFAULT now(),
  created_at timestamp without time zone DEFAULT now(),
  CONSTRAINT transfers_pkey PRIMARY KEY (id_transfer),
  CONSTRAINT transfers_created_by_user_fkey FOREIGN KEY (created_by_user) REFERENCES auth.users(id),
  CONSTRAINT transfers_id_payment_fkey FOREIGN KEY (id_payment) REFERENCES public.payments(id_payment)
);
```
**Comentarios:**
- Información de transferencias bancarias
- **Diferencias con esquema actual:**
  - `created_by_user` como `uuid` y referencia a `auth.users`
  - Campos como `character varying` en lugar de referencias a tabla `banks`
  - Status por defecto: 'Pending'

### 23. **users** - Usuarios del Sistema
```sql
CREATE TABLE public.users (
  username character varying,
  password character varying,
  email character varying,
  full_name character varying,
  created_by_user integer,
  role1 character varying,
  id_user integer NOT NULL DEFAULT nextval('users_id_user_seq'::regclass),
  created_at timestamp without time zone DEFAULT now(),
  updated_at timestamp without time zone DEFAULT now(),
  phone numeric,
  unique_id numeric,
  CONSTRAINT users_pkey PRIMARY KEY (id_user),
  CONSTRAINT users_created_by_user_fkey FOREIGN KEY (created_by_user) REFERENCES public.users(id_user)
);
```
**Comentarios:**
- Usuarios del sistema web/aplicación
- **Diferencias con esquema actual:**
  - `role1` en lugar de referencia a tabla `roles`
  - `phone` y `unique_id` como `numeric` en lugar de `character varying`
  - Incluye auditoría con `created_by_user`

### 24. **users_agent** - Usuarios del Agente
```sql
CREATE TABLE public.users_agent (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  created_at timestamp with time zone NOT NULL DEFAULT now(),
  type text CHECK (type = ANY (ARRAY['Administrador'::text, 'Secundario'::text])),
  name text,
  updated_at timestamp with time zone,
  phone character varying,
  status boolean,
  CONSTRAINT users_agent_pkey PRIMARY KEY (id)
);
```
**Comentarios:**
- **TABLA CRÍTICA**: Usuarios del agente de Telegram
- **Similar al esquema actual** con pequeñas diferencias en el orden de campos
- **Tipos:** 'Administrador' o 'Secundario'
- **Status:** TRUE (activo) o FALSE (inactivo)

---

## Principales Diferencias con el Esquema Actual

### **Tablas Nuevas en Esquema Actual:**
- `banks` - Bancos del sistema
- `generic_status` - Estados genéricos
- `inventory_movement_types` - Tipos de movimiento de inventario
- `letters` - Letras (versión actualizada de `letras`)
- `product_conditions` - Condiciones de producto
- `return_action_types` - Tipos de acción de devolución
- `roles` - Roles de usuario
- `status_caja` - Estado de caja (versión actualizada de `estado_caja`)

### **Tablas que No Existen en Esquema Actual:**
- `expenses` - Gastos del negocio
- `interactions` - Interacciones del sistema

### **Mejoras en Esquema Actual:**
1. **Normalización**: Referencias a tablas en lugar de campos de texto
2. **Auditoría**: Campos `created_by_user` en la mayoría de tablas
3. **Validaciones**: Constraints CHECK y referencias FK más estrictas
4. **Nomenclatura**: Corrección de typos y nombres más descriptivos
5. **Estructura**: Mejor organización de campos y tipos de datos

### **Campos Críticos Mantenidos:**
- `users_agent` - Estructura similar para usuarios del agente
- `sales_orders` y `sales_order_details` - Flujo principal de ventas
- `payment_plan` y `payment_installment` - Sistema de financiamiento
- `payments` - Tabla central de pagos

---

*Documento creado para referencia del esquema anterior de SOCOMAC - Fecha: $(date)*
