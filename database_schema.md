# Esquema de Base de Datos - SOCOMAC

Este documento contiene el esquema completo de la base de datos del sistema SOCOMAC para referencia y consultas futuras.

## ⚠️ ADVERTENCIA
Este esquema es solo para contexto y no está diseñado para ser ejecutado directamente. El orden de las tablas y las restricciones pueden no ser válidos para la ejecución.

---

## Tablas del Sistema

### 1. **banks** - Bancos
```sql
CREATE TABLE public.banks (
  id_bank integer NOT NULL DEFAULT nextval('banks_id_bank_seq'::regclass),
  name character varying NOT NULL,
  swift_code character varying UNIQUE,
  created_at timestamp without time zone NOT NULL DEFAULT now(),
  updated_at timestamp without time zone,
  CONSTRAINT banks_pkey PRIMARY KEY (id_bank)
);
```
**Comentarios:**
- Almacena información de bancos del sistema
- Incluye código SWIFT único para identificación internacional
- Usado en transferencias y cheques

### 2. **category** - Categorías de Productos
```sql
CREATE TABLE public.category (
  id_category integer NOT NULL DEFAULT nextval('category_id_category_seq'::regclass),
  name_category character varying,
  created_at timestamp without time zone,
  updated_at timestamp without time zone,
  CONSTRAINT category_pkey PRIMARY KEY (id_category)
);
```
**Comentarios:**
- Categorías para clasificar productos
- Relacionada con la tabla `products`

### 3. **checks** - Cheques
```sql
CREATE TABLE public.checks (
  id_check integer NOT NULL DEFAULT nextval('checks_id_check_seq'::regclass),
  id_payment integer,
  check_number character varying NOT NULL,
  id_emission_bank integer NOT NULL,
  emission_date date NOT NULL,
  due_date date,
  amount numeric NOT NULL,
  id_status integer,
  created_at timestamp without time zone NOT NULL DEFAULT now(),
  updated_at timestamp without time zone,
  id_destiny_bank integer,
  stimate_collection_date date,
  real_collection_date date,
  id_payment_plan integer,
  type text,
  CONSTRAINT checks_pkey PRIMARY KEY (id_check),
  CONSTRAINT checks_id_destiny_bank_fkey FOREIGN KEY (id_destiny_bank) REFERENCES public.banks(id_bank),
  CONSTRAINT checks_id_payment_fkey FOREIGN KEY (id_payment) REFERENCES public.payments(id_payment),
  CONSTRAINT checks_id_status_fkey FOREIGN KEY (id_status) REFERENCES public.generic_status(id_status),
  CONSTRAINT checks_id_payment_plan_fkey FOREIGN KEY (id_payment_plan) REFERENCES public.payment_plan(id_payment_plan)
);
```
**Comentarios:**
- Maneja información completa de cheques
- Incluye fechas de emisión, vencimiento y cobro estimado/real
- Relacionada con pagos y planes de pago

### 4. **classification** - Clasificaciones
```sql
CREATE TABLE public.classification (
  id_classification integer NOT NULL DEFAULT nextval('classification_id_classification_seq'::regclass),
  nombre character varying,
  primer_apellido character varying,
  segundo_apellido character varying,
  description text,
  examples character varying,
  comments text,
  type character varying,
  created_at timestamp without time zone,
  updated_at timestamp without time zone,
  CONSTRAINT classification_pkey PRIMARY KEY (id_classification)
);
```
**Comentarios:**
- Clasificaciones para órdenes de venta (Venta producto/Venta servicio)
- Incluye ejemplos y comentarios para claridad
- Usada en `sales_orders` y `payments`

### 5. **classification_notes** - Notas de Clasificación
```sql
CREATE TABLE public.classification_notes (
  id integer NOT NULL DEFAULT nextval('classification_notes_id_seq'::regclass),
  id_payment integer NOT NULL UNIQUE,
  id_classification integer NOT NULL,
  note text,
  created_at timestamp without time zone NOT NULL DEFAULT now(),
  created_by integer NOT NULL,
  CONSTRAINT classification_notes_pkey PRIMARY KEY (id),
  CONSTRAINT classification_notes_id_payment_fkey FOREIGN KEY (id_payment) REFERENCES public.payments(id_payment),
  CONSTRAINT classification_notes_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id_user),
  CONSTRAINT classification_notes_id_classification_fkey FOREIGN KEY (id_classification) REFERENCES public.classification(id_classification)
);
```
**Comentarios:**
- Notas adicionales para clasificaciones de pagos
- Relacionada con pagos y usuarios que crean las notas

### 6. **clients** - Clientes
```sql
CREATE TABLE public.clients (
  id_client integer NOT NULL DEFAULT nextval('clients_id_client_seq'::regclass),
  client_type character varying,
  unique_id character varying UNIQUE,
  full_name character varying,
  first_name character varying,
  last_name character varying,
  company character varying,
  address text,
  city character varying,
  department character varying,
  phone character varying,
  phone_2 character varying,
  email character varying,
  client_classification character varying,
  created_at timestamp without time zone,
  updated_at timestamp without time zone,
  created_by_user integer,
  CONSTRAINT clients_pkey PRIMARY KEY (id_client),
  CONSTRAINT clients_created_by_user_fkey FOREIGN KEY (created_by_user) REFERENCES public.users(id_user)
);
```
**Comentarios:**
- Información completa de clientes (personas naturales y empresas)
- Incluye múltiples teléfonos y clasificación de cliente
- Tabla central para el sistema de ventas

### 7. **generic_status** - Estados Genéricos
```sql
CREATE TABLE public.generic_status (
  id_status integer NOT NULL DEFAULT nextval('generic_status_id_status_seq'::regclass),
  entity_type character varying NOT NULL,
  name character varying NOT NULL,
  description text,
  created_at timestamp without time zone NOT NULL DEFAULT now(),
  updated_at timestamp without time zone,
  CONSTRAINT generic_status_pkey PRIMARY KEY (id_status)
);
```
**Comentarios:**
- Estados genéricos para diferentes entidades del sistema
- Usado en múltiples tablas para manejar estados

### 8. **inventory** - Inventario
```sql
CREATE TABLE public.inventory (
  id_inventory_movement integer NOT NULL DEFAULT nextval('inventory_id_inventory_movement_seq'::regclass),
  id_product integer,
  movement_date date,
  id_movement_type integer,
  quantity integer,
  notes text,
  created_at timestamp without time zone,
  updated_at timestamp without time zone,
  created_by_user integer,
  CONSTRAINT inventory_pkey PRIMARY KEY (id_inventory_movement),
  CONSTRAINT inventory_id_product_fkey FOREIGN KEY (id_product) REFERENCES public.products(id_product),
  CONSTRAINT inventory_created_by_user_fkey FOREIGN KEY (created_by_user) REFERENCES public.users(id_user)
);
```
**Comentarios:**
- Movimientos de inventario (entradas/salidas)
- Relacionada con productos y usuarios

### 9. **inventory_movement_types** - Tipos de Movimiento de Inventario
```sql
CREATE TABLE public.inventory_movement_types (
  id_movement_type integer NOT NULL DEFAULT nextval('inventory_movement_types_id_movement_type_seq'::regclass),
  name character varying NOT NULL,
  description text,
  created_at timestamp without time zone NOT NULL DEFAULT now(),
  updated_at timestamp without time zone,
  CONSTRAINT inventory_movement_types_pkey PRIMARY KEY (id_movement_type)
);
```
**Comentarios:**
- Tipos de movimientos de inventario (entrada, salida, ajuste, etc.)

### 10. **letters** - Letras
```sql
CREATE TABLE public.letters (
  id_letter integer NOT NULL DEFAULT nextval('letters_id_letter_seq'::regclass),
  letter_number character varying NOT NULL,
  due_date date NOT NULL,
  amount numeric NOT NULL,
  id_status integer,
  created_at timestamp without time zone NOT NULL DEFAULT now(),
  updated_at timestamp without time zone,
  id_payment_plan integer,
  CONSTRAINT letters_pkey PRIMARY KEY (id_letter),
  CONSTRAINT letters_id_status_fkey FOREIGN KEY (id_status) REFERENCES public.generic_status(id_status),
  CONSTRAINT letters_id_payment_plan_fkey FOREIGN KEY (id_payment_plan) REFERENCES public.payment_plan(id_payment_plan)
);
```
**Comentarios:**
- Letras de cambio para planes de financiamiento tipo "Letras"
- Relacionada con planes de pago

### 11. **payment_installment** - Cuotas de Pago
```sql
CREATE TABLE public.payment_installment (
  id_payment_installment integer NOT NULL DEFAULT nextval('payment_installment_id_payment_installment_seq'::regclass),
  id_payment_plan integer,
  installment_number integer,
  due_date date,
  amount numeric,
  id_status integer,
  pay_amount numeric,
  payment_date date,
  created_at timestamp without time zone,
  updated_at timestamp without time zone,
  early_payment_discount numeric,
  CONSTRAINT payment_installment_pkey PRIMARY KEY (id_payment_installment),
  CONSTRAINT payment_installment_id_payment_plan_fkey FOREIGN KEY (id_payment_plan) REFERENCES public.payment_plan(id_payment_plan)
);
```
**Comentarios:**
- Cuotas individuales de los planes de financiamiento
- Incluye descuentos por pago anticipado
- Tabla clave para el sistema de pagos

### 12. **payment_plan** - Planes de Pago
```sql
CREATE TABLE public.payment_plan (
  id_payment_plan integer NOT NULL DEFAULT nextval('payment_plan_id_payment_plan_seq'::regclass),
  id_sales_orders integer,
  num_installments integer,
  total_amount numeric,
  start_date date,
  frequency text,
  id_status integer,
  notes text,
  created_at timestamp without time zone,
  updated_at timestamp without time zone,
  type_payment_plan text,
  CONSTRAINT payment_plan_pkey PRIMARY KEY (id_payment_plan),
  CONSTRAINT payment_plan_id_sales_orders_fkey FOREIGN KEY (id_sales_orders) REFERENCES public.sales_orders(id_sales_orders)
);
```
**Comentarios:**
- Planes de financiamiento para órdenes de venta
- Tipos: "Letras" u "Otro plan de financiamiento"
- Relacionada con órdenes de venta

### 13. **payments** - Pagos
```sql
CREATE TABLE public.payments (
  id_payment integer NOT NULL DEFAULT nextval('payments_id_payment_seq'::regclass),
  id_sales_orders integer,
  id_payment_installment integer,
  id_status integer,
  amount numeric,
  payment_date date,
  id_destiny_bank integer,
  notes text,
  created_at timestamp without time zone,
  updated_at timestamp without time zone,
  caja_receipt character varying,
  id_client integer,
  id_classification integer,
  type character varying,
  origin_return_id bigint,
  created_by_user integer,
  CONSTRAINT payments_pkey PRIMARY KEY (id_payment),
  CONSTRAINT payments_id_client_fkey FOREIGN KEY (id_client) REFERENCES public.clients(id_client),
  CONSTRAINT payments_id_sales_orders_fkey FOREIGN KEY (id_sales_orders) REFERENCES public.sales_orders(id_sales_orders),
  CONSTRAINT payments_id_classification_fkey FOREIGN KEY (id_classification) REFERENCES public.classification(id_classification),
  CONSTRAINT payments_created_by_user_fkey FOREIGN KEY (created_by_user) REFERENCES public.users(id_user),
  CONSTRAINT payments_id_destiny_bank_fkey FOREIGN KEY (id_destiny_bank) REFERENCES public.banks(id_bank),
  CONSTRAINT payments_id_payment_installment_fkey FOREIGN KEY (id_payment_installment) REFERENCES public.payment_installment(id_payment_installment)
);
```
**Comentarios:**
- Tabla central de pagos del sistema
- Puede ser pago directo a orden o pago a cuota
- Incluye información de caja y clasificación

### 14. **product_conditions** - Condiciones de Producto
```sql
CREATE TABLE public.product_conditions (
  id_condition integer NOT NULL DEFAULT nextval('product_conditions_id_condition_seq'::regclass),
  name character varying NOT NULL UNIQUE,
  description text,
  created_at timestamp without time zone NOT NULL DEFAULT now(),
  updated_at timestamp without time zone,
  CONSTRAINT product_conditions_pkey PRIMARY KEY (id_condition)
);
```
**Comentarios:**
- Condiciones de productos (nuevo, usado, reacondicionado, etc.)

### 15. **products** - Productos
```sql
CREATE TABLE public.products (
  id_product integer NOT NULL DEFAULT nextval('products_id_product_seq'::regclass),
  name_product character varying NOT NULL,
  description text,
  id_condition integer NOT NULL,
  unit_price numeric NOT NULL,
  created_at timestamp without time zone NOT NULL DEFAULT now(),
  updated_at timestamp without time zone,
  factory_reference text,
  taxes text,
  id_category bigint NOT NULL,
  created_by_user integer,
  CONSTRAINT products_pkey PRIMARY KEY (id_product),
  CONSTRAINT products_created_by_user_fkey FOREIGN KEY (created_by_user) REFERENCES public.users(id_user),
  CONSTRAINT products_id_category_fkey FOREIGN KEY (id_category) REFERENCES public.category(id_category),
  CONSTRAINT products_id_condition_fkey FOREIGN KEY (id_condition) REFERENCES public.product_conditions(id_condition)
);
```
**Comentarios:**
- Catálogo de productos del sistema
- Incluye precios, referencias de fábrica e impuestos
- Relacionada con categorías y condiciones

### 16. **purchase_order_details** - Detalles de Órdenes de Compra
```sql
CREATE TABLE public.purchase_order_details (
  id_purchase_order_detail integer NOT NULL DEFAULT nextval('purchase_order_details_id_purchase_order_detail_seq'::regclass),
  id_purchase_order integer,
  id_product integer,
  quantity integer,
  unit_price numeric,
  subtotal numeric,
  created_at timestamp without time zone,
  updated_at timestamp without time zone,
  CONSTRAINT purchase_order_details_pkey PRIMARY KEY (id_purchase_order_detail),
  CONSTRAINT purchase_order_details_id_purchase_order_fkey FOREIGN KEY (id_purchase_order) REFERENCES public.purchase_orders(id_purchase_order),
  CONSTRAINT purchase_order_details_id_product_fkey FOREIGN KEY (id_product) REFERENCES public.products(id_product)
);
```
**Comentarios:**
- Detalles de productos en órdenes de compra
- Similar a `sales_order_details` pero para compras

### 17. **purchase_orders** - Órdenes de Compra
```sql
CREATE TABLE public.purchase_orders (
  id_purchase_order integer NOT NULL DEFAULT nextval('purchase_orders_id_purchase_order_seq'::regclass),
  id_supplier integer NOT NULL,
  order_date date NOT NULL,
  id_status integer,
  total numeric,
  notes text,
  created_at timestamp without time zone NOT NULL DEFAULT now(),
  updated_at timestamp without time zone,
  type text,
  origin_bank integer,
  identification_number numeric,
  emission_date date,
  id_classsification integer,
  CONSTRAINT purchase_orders_pkey PRIMARY KEY (id_purchase_order),
  CONSTRAINT purchase_orders_origin_bank_fkey FOREIGN KEY (origin_bank) REFERENCES public.banks(id_bank),
  CONSTRAINT purchase_orders_id_classsification_fkey FOREIGN KEY (id_classsification) REFERENCES public.classification(id_classification),
  CONSTRAINT purchase_orders_id_supplier_fkey FOREIGN KEY (id_supplier) REFERENCES public.suppliers(id_supplier)
);
```
**Comentarios:**
- Órdenes de compra a proveedores
- Incluye información bancaria y clasificación

### 18. **return_action_types** - Tipos de Acción de Devolución
```sql
CREATE TABLE public.return_action_types (
  id_action_type integer NOT NULL DEFAULT nextval('return_action_types_id_action_type_seq'::regclass),
  name character varying NOT NULL,
  description text,
  created_at timestamp without time zone NOT NULL DEFAULT now(),
  updated_at timestamp without time zone,
  CONSTRAINT return_action_types_pkey PRIMARY KEY (id_action_type)
);
```
**Comentarios:**
- Tipos de acciones para devoluciones (reembolso, cambio, crédito, etc.)

### 19. **returns_log** - Log de Devoluciones
```sql
CREATE TABLE public.returns_log (
  id_return bigint NOT NULL,
  id_sales_orders bigint,
  id_sales_order_detail bigint,
  id_client bigint,
  amount numeric,
  id_action_type integer,
  target_order_id bigint,
  target_quota_id bigint,
  id_status integer,
  notes text,
  created_at timestamp without time zone NOT NULL DEFAULT now(),
  quantity numeric,
  processed_amount numeric,
  CONSTRAINT returns_log_pkey PRIMARY KEY (id_return),
  CONSTRAINT returns_log_id_sales_order_detail_fkey FOREIGN KEY (id_sales_order_detail) REFERENCES public.sales_order_details(id_sales_order_detail),
  CONSTRAINT returns_log_target_quota_id_fkey FOREIGN KEY (target_quota_id) REFERENCES public.payment_installment(id_payment_installment),
  CONSTRAINT returns_log_target_order_id_fkey FOREIGN KEY (target_order_id) REFERENCES public.sales_orders(id_sales_orders),
  CONSTRAINT returns_log_id_client_fkey FOREIGN KEY (id_client) REFERENCES public.clients(id_client),
  CONSTRAINT returns_log_id_sales_orders_fkey FOREIGN KEY (id_sales_orders) REFERENCES public.sales_orders(id_sales_orders)
);
```
**Comentarios:**
- Registro de todas las devoluciones del sistema
- Incluye información de órdenes objetivo y cuotas afectadas

### 20. **roles** - Roles de Usuario
```sql
CREATE TABLE public.roles (
  id_role integer NOT NULL DEFAULT nextval('roles_id_role_seq'::regclass),
  name character varying NOT NULL UNIQUE,
  description text,
  created_at timestamp without time zone NOT NULL DEFAULT now(),
  updated_at timestamp without time zone,
  CONSTRAINT roles_pkey PRIMARY KEY (id_role)
);
```
**Comentarios:**
- Roles del sistema (Administrador, Vendedor, etc.)
- Usado en la tabla `users`

### 21. **sales_order_details** - Detalles de Órdenes de Venta
```sql
CREATE TABLE public.sales_order_details (
  id_sales_order_detail integer NOT NULL DEFAULT nextval('sales_order_details_id_sales_order_detail_seq'::regclass),
  id_sales_orders integer,
  id_product integer,
  quantity integer,
  unit_price bigint,
  subtotal bigint,
  created_at timestamp without time zone,
  updated_at timestamp without time zone,
  devolucion text,
  CONSTRAINT sales_order_details_pkey PRIMARY KEY (id_sales_order_detail),
  CONSTRAINT sales_order_details_id_product_fkey FOREIGN KEY (id_product) REFERENCES public.products(id_product),
  CONSTRAINT sales_order_details_id_sales_orders_fkey FOREIGN KEY (id_sales_orders) REFERENCES public.sales_orders(id_sales_orders)
);
```
**Comentarios:**
- Detalles de productos en órdenes de venta
- Campo `devolucion` para marcar productos devueltos
- Precios en bigint (considerar división por 1000)

### 22. **sales_orders** - Órdenes de Venta
```sql
CREATE TABLE public.sales_orders (
  id_sales_orders integer NOT NULL DEFAULT nextval('sales_orders_id_sales_orders_seq'::regclass),
  id_client integer,
  id_classification integer,
  order_date date,
  delivery_date date,
  id_status integer,
  total numeric,
  outstanding_balance numeric,
  percentage_paid numeric,
  notes text,
  created_at timestamp without time zone,
  updated_at timestamp without time zone,
  discount numeric,
  created_by_user integer,
  CONSTRAINT sales_orders_pkey PRIMARY KEY (id_sales_orders),
  CONSTRAINT sales_orders_created_by_user_fkey FOREIGN KEY (created_by_user) REFERENCES public.users(id_user),
  CONSTRAINT sales_orders_id_client_fkey FOREIGN KEY (id_client) REFERENCES public.clients(id_client),
  CONSTRAINT sales_orders_id_classification_fkey FOREIGN KEY (id_classification) REFERENCES public.classification(id_classification)
);
```
**Comentarios:**
- Tabla central de órdenes de venta
- Incluye balance pendiente y porcentaje pagado
- Relacionada con clientes y clasificaciones

### 23. **shipments** - Envíos
```sql
CREATE TABLE public.shipments (
  id_shipment integer NOT NULL DEFAULT nextval('shipments_id_shipment_seq'::regclass),
  id_sales_orders integer NOT NULL,
  tracking_number character varying UNIQUE,
  carrier character varying,
  shipping_date date,
  delivery_date date,
  status character varying,
  shipping_cost numeric,
  destination_address text,
  created_at timestamp without time zone NOT NULL DEFAULT now(),
  updated_at timestamp without time zone,
  CONSTRAINT shipments_pkey PRIMARY KEY (id_shipment),
  CONSTRAINT shipments_id_sales_orders_fkey FOREIGN KEY (id_sales_orders) REFERENCES public.sales_orders(id_sales_orders)
);
```
**Comentarios:**
- Información de envíos para órdenes de venta
- Incluye tracking y costos de envío

### 24. **status_caja** - Estado de Caja
```sql
CREATE TABLE public.status_caja (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  created_at timestamp with time zone NOT NULL DEFAULT now(),
  type text,
  amount numeric,
  status boolean,
  CONSTRAINT status_caja_pkey PRIMARY KEY (id)
);
```
**Comentarios:**
- **TABLA CRÍTICA**: Controla el estado de caja y conciliaciones bancarias
- **Estructura conocida:**
  - Fila 1: Caja (id=1)
  - Fila 2: Banco Davivienda (id=2)
  - Fila 3: Banco Bancolombia (id=3)
- **Estados:** TRUE (abierta) o FALSE (cerrada)

### 25. **supplier_product** - Productos de Proveedor
```sql
CREATE TABLE public.supplier_product (
  id_supplier_product integer NOT NULL DEFAULT nextval('supplier_product_id_supplier_product_seq'::regclass),
  id_supplier integer,
  id_product integer,
  cost_price numeric,
  lead_time_days integer,
  notes text,
  created_at timestamp without time zone,
  updated_at timestamp without time zone,
  CONSTRAINT supplier_product_pkey PRIMARY KEY (id_supplier_product),
  CONSTRAINT supplier_product_id_product_fkey FOREIGN KEY (id_product) REFERENCES public.products(id_product),
  CONSTRAINT supplier_product_id_supplier_fkey FOREIGN KEY (id_supplier) REFERENCES public.suppliers(id_supplier)
);
```
**Comentarios:**
- Relación entre proveedores y productos
- Incluye precios de costo y tiempos de entrega

### 26. **suppliers** - Proveedores
```sql
CREATE TABLE public.suppliers (
  id_supplier integer NOT NULL DEFAULT nextval('suppliers_id_supplier_seq'::regclass),
  company_name character varying,
  contact_name character varying,
  phone character varying,
  email character varying,
  website character varying,
  address character varying,
  notes text,
  created_at timestamp without time zone,
  updated_at timestamp without time zone,
  CONSTRAINT suppliers_pkey PRIMARY KEY (id_supplier)
);
```
**Comentarios:**
- Información de proveedores del sistema
- Usado en órdenes de compra

### 27. **transfers** - Transferencias
```sql
CREATE TABLE public.transfers (
  id_transfer integer NOT NULL DEFAULT nextval('transfers_id_transfer_seq'::regclass),
  id_payment integer,
  proof_number character varying,
  id_emission_bank integer,
  emission_date date,
  trans_value numeric,
  id_status integer,
  id_destiny_bank integer,
  observations text,
  updated_at timestamp without time zone,
  created_at timestamp without time zone,
  CONSTRAINT transfers_pkey PRIMARY KEY (id_transfer),
  CONSTRAINT transfers_id_destiny_bank_fkey FOREIGN KEY (id_destiny_bank) REFERENCES public.banks(id_bank),
  CONSTRAINT transfers_id_payment_fkey FOREIGN KEY (id_payment) REFERENCES public.payments(id_payment)
);
```
**Comentarios:**
- Información de transferencias bancarias
- Relacionada con pagos
- **Restricción importante:** Solo Bancolombia o Davivienda como banco destino

### 28. **users** - Usuarios del Sistema
```sql
CREATE TABLE public.users (
  id_user integer NOT NULL DEFAULT nextval('users_id_user_seq'::regclass),
  username character varying NOT NULL UNIQUE,
  password character varying NOT NULL,
  email character varying NOT NULL UNIQUE,
  id_role integer NOT NULL,
  full_name character varying NOT NULL,
  phone character varying,
  unique_id character varying,
  created_at timestamp without time zone NOT NULL DEFAULT now(),
  updated_at timestamp without time zone,
  CONSTRAINT users_pkey PRIMARY KEY (id_user),
  CONSTRAINT users_id_role_fkey FOREIGN KEY (id_role) REFERENCES public.roles(id_role)
);
```
**Comentarios:**
- Usuarios del sistema web/aplicación
- Relacionada con roles
- **Diferente de `users_agent`** (usuarios del agente de Telegram)

### 29. **users_agent** - Usuarios del Agente
```sql
CREATE TABLE public.users_agent (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  created_at timestamp with time zone NOT NULL DEFAULT now(),
  type text CHECK (type = ANY (ARRAY['Administrador'::text, 'Secundario'::text])),
  name text,
  phone character varying,
  status boolean,
  updated_at timestamp with time zone,
  CONSTRAINT users_agent_pkey PRIMARY KEY (id)
);
```
**Comentarios:**
- **TABLA CRÍTICA**: Usuarios del agente de Telegram
- **Tipos:** 'Administrador' o 'Secundario'
- **Status:** TRUE (activo) o FALSE (inactivo)
- **Regla importante:** Solo puede haber un usuario activo a la vez
- **Diferente de `users`** (usuarios del sistema web)

---

## Relaciones Clave

### Flujo Principal de Ventas:
1. **clients** → **sales_orders** → **sales_order_details**
2. **sales_orders** → **payment_plan** → **payment_installment**
3. **payments** → **payment_installment** (pagos a cuotas)
4. **payments** → **sales_orders** (pagos directos)

### Flujo de Pagos:
- **payments** → **transfers** (transferencias)
- **payments** → **checks** (cheques)
- **payments** → **banks** (bancos destino)

### Gestión de Usuarios:
- **users_agent**: Usuarios del agente de Telegram
- **users**: Usuarios del sistema web
- **roles**: Roles del sistema

---

## Notas Importantes

1. **División por 1000**: Los precios en `sales_order_details` están en bigint y pueden requerir división por 1000
2. **Status de Caja**: Solo se pueden procesar pagos cuando la caja está abierta
3. **Usuarios Activos**: Solo puede haber un usuario activo en `users_agent` a la vez
4. **Bancos Destino**: Para transferencias, solo se permiten Bancolombia o Davivienda
5. **Devoluciones**: Se marcan en el campo `devolucion` de `sales_order_details`
6. **Planes de Financiamiento**: Dos tipos - "Letras" y "Otro plan de financiamiento"

---

*Documento creado para referencia del sistema SOCOMAC - Fecha: $(date)*
