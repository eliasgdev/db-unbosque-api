-- ============================================================================
-- 01_DDL_TABLAS.SQL — ESQUEMA POSTGRESQL (12 ENTIDADES EN 3FN)
-- Universidad El Bosque · Ingeniería de Sistemas · Bases de Datos 1
-- ============================================================================

CREATE EXTENSION IF NOT EXISTS btree_gist;

-- ----------------------------------------------------------------------------
-- 1. MONEDA
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS moneda (
    id_moneda BIGINT GENERATED ALWAYS AS IDENTITY,
    codigo VARCHAR(3) NOT NULL,
    nombre VARCHAR(60) NOT NULL,
    simbolo VARCHAR(5) NOT NULL,
    CONSTRAINT pk_moneda PRIMARY KEY (id_moneda),
    CONSTRAINT uq_moneda_codigo UNIQUE (codigo),
    CONSTRAINT ck_moneda_codigo_len CHECK (char_length(trim(codigo)) = 3)
);

-- ----------------------------------------------------------------------------
-- 2. EMPRESA
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS empresa (
    id_empresa BIGINT GENERATED ALWAYS AS IDENTITY,
    nit VARCHAR(20) NOT NULL,
    razon_social VARCHAR(200) NOT NULL,
    id_moneda BIGINT NOT NULL,
    CONSTRAINT pk_empresa PRIMARY KEY (id_empresa),
    CONSTRAINT uq_empresa_nit UNIQUE (nit),
    CONSTRAINT fk_empresa_moneda FOREIGN KEY (id_moneda)
        REFERENCES moneda (id_moneda)
        ON UPDATE RESTRICT ON DELETE RESTRICT
);

-- ----------------------------------------------------------------------------
-- 3. PERIODO_CONTABLE
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS periodo_contable (
    id_periodo BIGINT GENERATED ALWAYS AS IDENTITY,
    id_empresa BIGINT NOT NULL,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    estado VARCHAR(10) NOT NULL DEFAULT 'ABIERTO',
    CONSTRAINT pk_periodo_contable PRIMARY KEY (id_periodo),
    CONSTRAINT fk_periodo_empresa FOREIGN KEY (id_empresa)
        REFERENCES empresa (id_empresa)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    CONSTRAINT ck_periodo_fechas CHECK (fecha_fin > fecha_inicio),
    CONSTRAINT ck_periodo_estado CHECK (estado IN ('ABIERTO', 'CERRADO')),
    CONSTRAINT ex_periodo_sin_traslape EXCLUDE USING gist (
        id_empresa WITH =,
        daterange(fecha_inicio, fecha_fin, '[]') WITH &&
    )
);

-- ----------------------------------------------------------------------------
-- 4. TIPO_CUENTA
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS tipo_cuenta (
    id_tipo_cuenta BIGINT GENERATED ALWAYS AS IDENTITY,
    clase VARCHAR(15) NOT NULL,
    naturaleza VARCHAR(7) NOT NULL,
    CONSTRAINT pk_tipo_cuenta PRIMARY KEY (id_tipo_cuenta),
    -- Una clase admite ambas naturalezas para las contracuentas
    -- (ej. Depreciación Acumulada = ACTIVO con naturaleza CREDITO).
    CONSTRAINT uq_tipo_cuenta_clase_naturaleza UNIQUE (clase, naturaleza),
    CONSTRAINT ck_tipo_cuenta_clase CHECK (
        clase IN ('ACTIVO', 'PASIVO', 'PATRIMONIO', 'INGRESO', 'COSTO', 'GASTO')
    ),
    CONSTRAINT ck_tipo_cuenta_naturaleza CHECK (
        naturaleza IN ('DEBITO', 'CREDITO')
    )
);

-- ----------------------------------------------------------------------------
-- 5. RUBRO_ESTADO
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS rubro_estado (
    id_rubro BIGINT GENERATED ALWAYS AS IDENTITY,
    id_rubro_padre BIGINT NULL,
    codigo VARCHAR(20) NOT NULL,
    nombre VARCHAR(150) NOT NULL,
    estado_financiero VARCHAR(10) NOT NULL,
    orden SMALLINT NOT NULL,
    CONSTRAINT pk_rubro_estado PRIMARY KEY (id_rubro),
    CONSTRAINT uq_rubro_estado_codigo UNIQUE (codigo),
    CONSTRAINT fk_rubro_estado_padre FOREIGN KEY (id_rubro_padre)
        REFERENCES rubro_estado (id_rubro)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    CONSTRAINT ck_rubro_estado_financiero CHECK (
        estado_financiero IN ('BALANCE', 'RESULTADOS')
    ),
    CONSTRAINT ck_rubro_no_autorreferencia CHECK (
        id_rubro_padre IS NULL OR id_rubro_padre <> id_rubro
    )
);

-- ----------------------------------------------------------------------------
-- 6. PLAN_CUENTA
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS plan_cuenta (
    id_cuenta BIGINT GENERATED ALWAYS AS IDENTITY,
    id_empresa BIGINT NOT NULL,
    id_cuenta_padre BIGINT NULL,
    id_tipo_cuenta BIGINT NOT NULL,
    id_rubro BIGINT NOT NULL,
    codigo VARCHAR(20) NOT NULL,
    nombre VARCHAR(150) NOT NULL,
    nivel SMALLINT NOT NULL,
    acepta_movimiento BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT pk_plan_cuenta PRIMARY KEY (id_cuenta),
    CONSTRAINT uq_plan_cuenta_empresa_codigo UNIQUE (id_empresa, codigo),
    CONSTRAINT uq_plan_cuenta_empresa_id UNIQUE (id_empresa, id_cuenta),
    CONSTRAINT fk_plan_cuenta_empresa FOREIGN KEY (id_empresa)
        REFERENCES empresa (id_empresa)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    -- La cuenta padre debe pertenecer a la misma empresa que la cuenta hija.
    CONSTRAINT fk_plan_cuenta_padre FOREIGN KEY (id_empresa, id_cuenta_padre)
        REFERENCES plan_cuenta (id_empresa, id_cuenta)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    CONSTRAINT fk_plan_cuenta_tipo FOREIGN KEY (id_tipo_cuenta)
        REFERENCES tipo_cuenta (id_tipo_cuenta)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    CONSTRAINT fk_plan_cuenta_rubro FOREIGN KEY (id_rubro)
        REFERENCES rubro_estado (id_rubro)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    CONSTRAINT ck_plan_cuenta_nivel CHECK (nivel >= 1),
    CONSTRAINT ck_plan_cuenta_no_autorreferencia CHECK (
        id_cuenta_padre IS NULL OR id_cuenta_padre <> id_cuenta
    )
);

-- ----------------------------------------------------------------------------
-- 7. TIPO_ASIENTO
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS tipo_asiento (
    id_tipo_asiento BIGINT GENERATED ALWAYS AS IDENTITY,
    nombre VARCHAR(10) NOT NULL,
    CONSTRAINT pk_tipo_asiento PRIMARY KEY (id_tipo_asiento),
    CONSTRAINT uq_tipo_asiento_nombre UNIQUE (nombre),
    CONSTRAINT ck_tipo_asiento_nombre CHECK (
        nombre IN ('APERTURA', 'DIARIO', 'AJUSTE', 'CIERRE')
    )
);

-- ----------------------------------------------------------------------------
-- 8. ASIENTO
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS asiento (
    id_asiento BIGINT GENERATED ALWAYS AS IDENTITY,
    id_periodo BIGINT NOT NULL,
    id_tipo_asiento BIGINT NOT NULL,
    numero INTEGER NOT NULL,
    fecha DATE NOT NULL,
    descripcion VARCHAR(300) NOT NULL,
    estado VARCHAR(13) NOT NULL DEFAULT 'BORRADOR',
    CONSTRAINT pk_asiento PRIMARY KEY (id_asiento),
    CONSTRAINT uq_asiento_periodo_numero UNIQUE (id_periodo, numero),
    CONSTRAINT fk_asiento_periodo FOREIGN KEY (id_periodo)
        REFERENCES periodo_contable (id_periodo)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    CONSTRAINT fk_asiento_tipo FOREIGN KEY (id_tipo_asiento)
        REFERENCES tipo_asiento (id_tipo_asiento)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    CONSTRAINT ck_asiento_numero_positivo CHECK (numero > 0),
    CONSTRAINT ck_asiento_estado CHECK (
        estado IN ('BORRADOR', 'CONTABILIZADO')
    )
);

-- ----------------------------------------------------------------------------
-- 9. TERCERO
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS tercero (
    id_tercero BIGINT GENERATED ALWAYS AS IDENTITY,
    id_empresa BIGINT NOT NULL,
    documento VARCHAR(20) NOT NULL,
    nombre VARCHAR(200) NOT NULL,
    tipo VARCHAR(10) NOT NULL,
    CONSTRAINT pk_tercero PRIMARY KEY (id_tercero),
    CONSTRAINT uq_tercero_empresa_documento UNIQUE (id_empresa, documento),
    CONSTRAINT fk_tercero_empresa FOREIGN KEY (id_empresa)
        REFERENCES empresa (id_empresa)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    CONSTRAINT ck_tercero_tipo CHECK (
        tipo IN ('CLIENTE', 'PROVEEDOR', 'OTRO')
    )
);

-- ----------------------------------------------------------------------------
-- 10. CENTRO_COSTO
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS centro_costo (
    id_centro_costo BIGINT GENERATED ALWAYS AS IDENTITY,
    id_empresa BIGINT NOT NULL,
    codigo VARCHAR(20) NOT NULL,
    nombre VARCHAR(150) NOT NULL,
    CONSTRAINT pk_centro_costo PRIMARY KEY (id_centro_costo),
    CONSTRAINT uq_centro_costo_empresa_codigo UNIQUE (id_empresa, codigo),
    CONSTRAINT fk_centro_costo_empresa FOREIGN KEY (id_empresa)
        REFERENCES empresa (id_empresa)
        ON UPDATE RESTRICT ON DELETE RESTRICT
);

-- ----------------------------------------------------------------------------
-- 11. MOVIMIENTO
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS movimiento (
    id_movimiento BIGINT GENERATED ALWAYS AS IDENTITY,
    id_asiento BIGINT NOT NULL,
    id_cuenta BIGINT NOT NULL,
    id_tercero BIGINT NULL,
    id_centro_costo BIGINT NULL,
    debe NUMERIC(20, 2) NOT NULL DEFAULT 0.00,
    haber NUMERIC(20, 2) NOT NULL DEFAULT 0.00,
    CONSTRAINT pk_movimiento PRIMARY KEY (id_movimiento),
    CONSTRAINT fk_movimiento_asiento FOREIGN KEY (id_asiento)
        REFERENCES asiento (id_asiento)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    CONSTRAINT fk_movimiento_cuenta FOREIGN KEY (id_cuenta)
        REFERENCES plan_cuenta (id_cuenta)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    CONSTRAINT fk_movimiento_tercero FOREIGN KEY (id_tercero)
        REFERENCES tercero (id_tercero)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    CONSTRAINT fk_movimiento_centro_costo FOREIGN KEY (id_centro_costo)
        REFERENCES centro_costo (id_centro_costo)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    CONSTRAINT ck_movimiento_no_negativos CHECK (debe >= 0 AND haber >= 0),
    CONSTRAINT ck_movimiento_debe_o_haber_exclusivo CHECK (
        (debe > 0 AND haber = 0) OR (haber > 0 AND debe = 0)
    )
);

-- ----------------------------------------------------------------------------
-- 12. CIERRE_PERIODO
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS cierre_periodo (
    id_cierre BIGINT GENERATED ALWAYS AS IDENTITY,
    id_periodo BIGINT NOT NULL,
    id_asiento_cierre BIGINT NULL,
    utilidad_neta NUMERIC(20, 2) NOT NULL,
    fecha_cierre TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_cierre_periodo PRIMARY KEY (id_cierre),
    CONSTRAINT uq_cierre_periodo_id_periodo UNIQUE (id_periodo),
    CONSTRAINT uq_cierre_periodo_id_asiento UNIQUE (id_asiento_cierre),
    CONSTRAINT fk_cierre_periodo FOREIGN KEY (id_periodo)
        REFERENCES periodo_contable (id_periodo)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    CONSTRAINT fk_cierre_asiento FOREIGN KEY (id_asiento_cierre)
        REFERENCES asiento (id_asiento)
        ON UPDATE RESTRICT ON DELETE RESTRICT
);

-- ----------------------------------------------------------------------------
-- 13. ÍNDICES SOBRE LLAVES FORÁNEAS
-- PostgreSQL no indexa automáticamente las FK; los reportes las recorren.
-- ----------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS ix_asiento_periodo ON asiento (id_periodo);
CREATE INDEX IF NOT EXISTS ix_movimiento_asiento ON movimiento (id_asiento);
CREATE INDEX IF NOT EXISTS ix_movimiento_cuenta ON movimiento (id_cuenta);
CREATE INDEX IF NOT EXISTS ix_plan_cuenta_padre ON plan_cuenta (id_cuenta_padre);
CREATE INDEX IF NOT EXISTS ix_plan_cuenta_rubro ON plan_cuenta (id_rubro);
