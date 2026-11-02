-- ============================================================================
-- 02_SEED_DATOS_REALISTAS.SQL — CARGA MASIVA Y REALISTA DEL SISTEMA CONTABLE
-- Universidad El Bosque · Ingeniería de Sistemas · Bases de Datos 1
--
-- Contenido del dataset:
--   * 6 Monedas ISO 4217 (COP, USD, EUR, MXN, BRL, GBP)
--   * 6 Tipos de cuenta (ACTIVO, PASIVO, PATRIMONIO, INGRESO, COSTO, GASTO)
--   * 4 Tipos de asiento (APERTURA, DIARIO, AJUSTE, CIERRE)
--   * 21 Rubros de estados financieros en jerarquía de 3 niveles (BALANCE y RESULTADOS)
--   * 4 Empresas colombianas de distintos sectores económicos
--   * 10 Periodos contables (históricos CERRADO y vigentes ABIERTO)
--   * 111 Cuentas contables (PUC colombiano de 4 niveles: Clase -> Grupo -> Cuenta -> Subcuenta)
--   * 30 Terceros (clientes corporativos, proveedores, bancos, EPS/AFP, empleados)
--   * 15 Centros de costo por áreas operativas, comerciales y administrativas
--   * 32 Asientos contables y +115 Movimientos con partida doble exacta al centavo
--   * 4 Cierres de periodo registrados en CIERRE_PERIODO con sus asientos de CIERRE
-- ============================================================================

BEGIN;

TRUNCATE TABLE
    cierre_periodo,
    movimiento,
    asiento,
    centro_costo,
    tercero,
    plan_cuenta,
    rubro_estado,
    tipo_asiento,
    tipo_cuenta,
    periodo_contable,
    empresa,
    moneda
RESTART IDENTITY CASCADE;

-- ============================================================================
-- 1. MONEDA (IDs: 1..6)
-- ============================================================================
INSERT INTO moneda (codigo, nombre, simbolo) VALUES
    ('COP', 'Peso Colombiano', '$'),
    ('USD', 'Dólar Estadounidense', 'US$'),
    ('EUR', 'Euro', '€'),
    ('MXN', 'Peso Mexicano', 'Mex$'),
    ('BRL', 'Real Brasileño', 'R$'),
    ('GBP', 'Libra Esterlina', '£');

-- ============================================================================
-- 2. TIPO_CUENTA (IDs: 1..7)
-- ============================================================================
INSERT INTO tipo_cuenta (clase, naturaleza) VALUES
    ('ACTIVO', 'DEBITO'),       -- ID 1
    ('PASIVO', 'CREDITO'),      -- ID 2
    ('PATRIMONIO', 'CREDITO'),  -- ID 3
    ('INGRESO', 'CREDITO'),     -- ID 4
    ('COSTO', 'DEBITO'),        -- ID 5
    ('GASTO', 'DEBITO'),        -- ID 6
    ('ACTIVO', 'CREDITO');      -- ID 7: contracuentas de activo (depreciación, deterioro)

-- ============================================================================
-- 3. TIPO_ASIENTO (IDs: 1..4)
-- ============================================================================
INSERT INTO tipo_asiento (nombre) VALUES
    ('APERTURA'),  -- ID 1
    ('DIARIO'),    -- ID 2
    ('AJUSTE'),    -- ID 3
    ('CIERRE');    -- ID 4

-- ============================================================================
-- 4. RUBRO_ESTADO (21 rubros jerárquicos para BALANCE y RESULTADOS)
-- ============================================================================
-- Nivel 1: Raíces de Balance General (IDs 1..3)
INSERT INTO rubro_estado (id_rubro_padre, codigo, nombre, estado_financiero, orden) VALUES
    (NULL, 'BG-ACT', 'ACTIVO', 'BALANCE', 1),                                  -- ID 1
    (NULL, 'BG-PAS', 'PASIVO', 'BALANCE', 2),                                  -- ID 2
    (NULL, 'BG-PAT', 'PATRIMONIO', 'BALANCE', 3);                              -- ID 3

-- Nivel 2: Subrubros principales de Balance General (IDs 4..10)
INSERT INTO rubro_estado (id_rubro_padre, codigo, nombre, estado_financiero, orden) VALUES
    (1, 'BG-ACT-CORR', 'Activo Corriente', 'BALANCE', 1),                      -- ID 4
    (1, 'BG-ACT-NCORR', 'Activo No Corriente', 'BALANCE', 2),                  -- ID 5
    (2, 'BG-PAS-CORR', 'Pasivo Corriente', 'BALANCE', 1),                      -- ID 6
    (2, 'BG-PAS-LP', 'Pasivo a Largo Plazo', 'BALANCE', 2),                    -- ID 7
    (3, 'BG-PAT-CAP', 'Capital Social', 'BALANCE', 1),                         -- ID 8
    (3, 'BG-PAT-RESV', 'Reservas', 'BALANCE', 2),                              -- ID 9
    (3, 'BG-PAT-RES', 'Resultados del Ejercicio y Acumulados', 'BALANCE', 3);  -- ID 10

-- Nivel 3: Subrubros detallados de Balance General (IDs 11..15)
INSERT INTO rubro_estado (id_rubro_padre, codigo, nombre, estado_financiero, orden) VALUES
    (4, 'BG-ACT-EFE', 'Efectivo y Equivalentes de Efectivo', 'BALANCE', 1),    -- ID 11
    (4, 'BG-ACT-DEU', 'Deudores Comerciales y Cuentas por Cobrar', 'BALANCE', 2), -- ID 12
    (4, 'BG-ACT-INV', 'Inventarios Corrientes', 'BALANCE', 3),                 -- ID 13
    (5, 'BG-ACT-PPE', 'Propiedades, Planta y Equipo Neto', 'BALANCE', 1),      -- ID 14
    (6, 'BG-PAS-OP', 'Proveedores, Cuentas por Pagar y Obligaciones Laborales', 'BALANCE', 1); -- ID 15

-- Rubros de Estado de Resultados (IDs 16..21)
INSERT INTO rubro_estado (id_rubro_padre, codigo, nombre, estado_financiero, orden) VALUES
    (NULL, 'ER-ING-OPER', 'Ingresos Operacionales', 'RESULTADOS', 1),          -- ID 16
    (NULL, 'ER-COS-VTA', 'Costo de Ventas y de Prestación de Servicios', 'RESULTADOS', 2), -- ID 17
    (NULL, 'ER-GAS-OPER-ADM', 'Gastos Operacionales de Administración', 'RESULTADOS', 3),  -- ID 18
    (NULL, 'ER-GAS-OPER-VTA', 'Gastos Operacionales de Ventas', 'RESULTADOS', 4),          -- ID 19
    (NULL, 'ER-ING-NOPER', 'Ingresos No Operacionales (Financieros y Otros)', 'RESULTADOS', 5), -- ID 20
    (NULL, 'ER-GAS-NOPER', 'Gastos No Operacionales (Financieros)', 'RESULTADOS', 6);      -- ID 21

-- ============================================================================
-- 5. EMPRESA (4 Empresas Colombianas, IDs 1..4)
-- ============================================================================
INSERT INTO empresa (nit, razon_social, id_moneda) VALUES
    ('901458231-6', 'Comercializadora Sabana Norte S.A.S.', 1),     -- ID 1 (COP)
    ('900874129-3', 'Soluciones Clínicas El Bosque Ltda.', 1),      -- ID 2 (COP)
    ('890102345-8', 'Agroindustria Cafetera del Quindío S.A.', 1),  -- ID 3 (COP)
    ('901789456-2', 'Consultoría e Ingeniería Andina S.A.S.', 2);   -- ID 4 (USD)

-- ============================================================================
-- 6. PERIODO_CONTABLE (10 Periodos Contables, IDs 1..10)
-- ============================================================================
INSERT INTO periodo_contable (id_empresa, fecha_inicio, fecha_fin, estado) VALUES
    -- Empresa 1: Comercializadora Sabana Norte S.A.S.
    (1, '2024-01-01', '2024-12-31', 'CERRADO'),  -- ID 1
    (1, '2025-01-01', '2025-12-31', 'CERRADO'),  -- ID 2
    (1, '2026-01-01', '2026-12-31', 'ABIERTO'),  -- ID 3
    -- Empresa 2: Soluciones Clínicas El Bosque Ltda.
    (2, '2025-01-01', '2025-12-31', 'CERRADO'),  -- ID 4
    (2, '2026-01-01', '2026-06-30', 'CERRADO'),  -- ID 5
    (2, '2026-07-01', '2026-12-31', 'ABIERTO'),  -- ID 6
    -- Empresa 3: Agroindustria Cafetera del Quindío S.A.
    (3, '2025-01-01', '2025-12-31', 'CERRADO'),  -- ID 7
    (3, '2026-01-01', '2026-12-31', 'ABIERTO'),  -- ID 8
    -- Empresa 4: Consultoría e Ingeniería Andina S.A.S.
    (4, '2025-01-01', '2025-12-31', 'CERRADO'),  -- ID 9
    (4, '2026-01-01', '2026-12-31', 'ABIERTO');  -- ID 10

-- ============================================================================
-- 7. PLAN_CUENTA — EMPRESA 1 (66 Cuentas en 4 Niveles, IDs 1..66)
-- ============================================================================
-- Nivel 1: Clases (IDs 1..6)
INSERT INTO plan_cuenta (id_empresa, id_cuenta_padre, id_tipo_cuenta, id_rubro, codigo, nombre, nivel, acepta_movimiento) VALUES
    (1, NULL, 1, 1, '1', 'Activo', 1, FALSE),                                  -- ID 1
    (1, NULL, 2, 2, '2', 'Pasivo', 1, FALSE),                                  -- ID 2
    (1, NULL, 3, 3, '3', 'Patrimonio', 1, FALSE),                              -- ID 3
    (1, NULL, 4, 16, '4', 'Ingresos', 1, FALSE),                               -- ID 4
    (1, NULL, 6, 18, '5', 'Gastos', 1, FALSE),                                 -- ID 5
    (1, NULL, 5, 17, '6', 'Costos de Ventas', 1, FALSE);                       -- ID 6

-- Nivel 2: Grupos (IDs 7..22)
INSERT INTO plan_cuenta (id_empresa, id_cuenta_padre, id_tipo_cuenta, id_rubro, codigo, nombre, nivel, acepta_movimiento) VALUES
    (1, 1, 1, 11, '11', 'Efectivo y Equivalentes al Efectivo', 2, FALSE),      -- ID 7
    (1, 1, 1, 11, '12', 'Inversiones e Instrumentos Financieros', 2, FALSE),   -- ID 8
    (1, 1, 1, 12, '13', 'Deudores Comerciales y Otras Cuentas por Cobrar', 2, FALSE), -- ID 9
    (1, 1, 1, 13, '14', 'Inventarios', 2, FALSE),                              -- ID 10
    (1, 1, 1, 14, '15', 'Propiedades, Planta y Equipo', 2, FALSE),             -- ID 11
    (1, 2, 2, 7,  '21', 'Obligaciones Financieras', 2, FALSE),                 -- ID 12
    (1, 2, 2, 15, '22', 'Proveedores', 2, FALSE),                              -- ID 13
    (1, 2, 2, 15, '23', 'Cuentas por Pagar', 2, FALSE),                        -- ID 14
    (1, 2, 2, 15, '25', 'Obligaciones Laborales', 2, FALSE),                   -- ID 15
    (1, 3, 3, 8,  '31', 'Capital Social', 2, FALSE),                           -- ID 16
    (1, 3, 3, 9,  '33', 'Reservas', 2, FALSE),                                 -- ID 17
    (1, 3, 3, 10, '36', 'Resultados del Ejercicio', 2, FALSE),                 -- ID 18
    (1, 3, 3, 10, '37', 'Resultados de Ejercicios Anteriores', 2, FALSE),      -- ID 19
    (1, 4, 4, 16, '41', 'Ingresos Operacionales', 2, FALSE),                   -- ID 20
    (1, 4, 4, 20, '42', 'Ingresos No Operacionales', 2, FALSE),                -- ID 21
    (1, 5, 6, 18, '51', 'Gastos Operacionales de Administración', 2, FALSE);   -- ID 22

INSERT INTO plan_cuenta (id_empresa, id_cuenta_padre, id_tipo_cuenta, id_rubro, codigo, nombre, nivel, acepta_movimiento) VALUES
    (1, 5, 6, 19, '52', 'Gastos Operacionales de Ventas', 2, FALSE),           -- ID 23
    (1, 5, 6, 21, '53', 'Gastos No Operacionales', 2, FALSE),                  -- ID 24
    (1, 6, 5, 17, '61', 'Costo de Ventas y de Prestación de Servicios', 2, FALSE); -- ID 25

-- Nivel 3: Cuentas Mayores (IDs 26..48)
INSERT INTO plan_cuenta (id_empresa, id_cuenta_padre, id_tipo_cuenta, id_rubro, codigo, nombre, nivel, acepta_movimiento) VALUES
    (1, 7,  1, 11, '1105', 'Caja', 3, FALSE),                                  -- ID 26
    (1, 7,  1, 11, '1110', 'Bancos Nacionales', 3, FALSE),                     -- ID 27
    (1, 8,  1, 11, '1225', 'Certificados de Depósito a Término (CDT)', 3, FALSE), -- ID 28
    (1, 9,  1, 12, '1305', 'Clientes', 3, FALSE),                              -- ID 29
    (1, 10, 1, 13, '1435', 'Mercancías no Fabricadas por la Empresa', 3, FALSE), -- ID 30
    (1, 11, 1, 14, '1524', 'Equipo de Oficina', 3, FALSE),                     -- ID 31
    (1, 11, 1, 14, '1528', 'Equipo de Computación y Comunicación', 3, FALSE),  -- ID 32
    (1, 11, 1, 14, '1540', 'Flota y Equipo de Transporte', 3, FALSE),          -- ID 33
    (1, 11, 7, 14, '1592', 'Depreciación Acumulada', 3, FALSE),                -- ID 34
    (1, 12, 2, 7,  '2105', 'Bancos Nacionales - Pagarés', 3, FALSE),           -- ID 35
    (1, 13, 2, 15, '2205', 'Proveedores Nacionales', 3, FALSE),                -- ID 36
    (1, 14, 2, 15, '2335', 'Costos y Gastos por Pagar', 3, FALSE),             -- ID 37
    (1, 15, 2, 15, '2505', 'Salarios y Prestaciones por Pagar', 3, FALSE),     -- ID 38
    (1, 16, 3, 8,  '3105', 'Capital Suscrito y Pagado', 3, FALSE),             -- ID 39
    (1, 17, 3, 9,  '3305', 'Reservas Obligatorias', 3, FALSE),                 -- ID 40
    (1, 18, 3, 10, '3605', 'Utilidad del Ejercicio', 3, FALSE),                -- ID 41
    (1, 19, 3, 10, '3705', 'Utilidades Acumuladas', 3, FALSE),                 -- ID 42
    (1, 20, 4, 16, '4135', 'Comercio al por Mayor y al por Menor', 3, FALSE),  -- ID 43
    (1, 20, 4, 16, '4155', 'Actividades Inmobiliarias, Empresariales y de Consultoría', 3, FALSE), -- ID 44
    (1, 21, 4, 20, '4210', 'Ingresos Financieros', 3, FALSE),                  -- ID 45
    (1, 22, 6, 18, '5105', 'Gastos de Personal Administrativo', 3, FALSE),     -- ID 46
    (1, 22, 6, 18, '5110', 'Honorarios Administrativos', 3, FALSE),            -- ID 47
    (1, 22, 6, 18, '5120', 'Arrendamientos', 3, FALSE),                        -- ID 48
    (1, 22, 6, 18, '5135', 'Servicios Públicos y Conectividad', 3, FALSE),     -- ID 49
    (1, 22, 6, 18, '5145', 'Mantenimiento y Reparaciones', 3, FALSE),          -- ID 50
    (1, 22, 6, 18, '5160', 'Depreciaciones Administrativas', 3, FALSE),        -- ID 51
    (1, 23, 6, 19, '5205', 'Gastos de Personal de Ventas', 3, FALSE),          -- ID 52
    (1, 23, 6, 19, '5235', 'Publicidad, Propaganda y Promoción', 3, FALSE),    -- ID 53
    (1, 24, 6, 21, '5305', 'Gastos Bancarios y Financieros', 3, FALSE),        -- ID 54
    (1, 25, 5, 17, '6135', 'Costo de Ventas de Mercancías', 3, FALSE);         -- ID 55

-- Nivel 4: Subcuentas Hoja para Empresa 1 (IDs 56..83, acepta_movimiento = TRUE)
INSERT INTO plan_cuenta (id_empresa, id_cuenta_padre, id_tipo_cuenta, id_rubro, codigo, nombre, nivel, acepta_movimiento) VALUES
    (1, 26, 1, 11, '110505', 'Caja General Bogotá', 4, TRUE),                                    -- ID 56
    (1, 26, 1, 11, '110510', 'Caja Menor Administración', 4, TRUE),                              -- ID 57
    (1, 27, 1, 11, '111005', 'Banco de Bogotá - Cuenta Corriente 458-99012-3', 4, TRUE),         -- ID 58
    (1, 27, 1, 11, '111010', 'Bancolombia - Cuenta de Ahorros 031-784512-9', 4, TRUE),           -- ID 59
    (1, 28, 1, 11, '122505', 'CDT Davivienda 90 Días', 4, TRUE),                                 -- ID 60
    (1, 29, 1, 12, '130505', 'Clientes Nacionales Corporativos', 4, TRUE),                       -- ID 61
    (1, 30, 1, 13, '143505', 'Inventario de Servidores y Equipos de Red', 4, TRUE),              -- ID 62
    (1, 30, 1, 13, '143510', 'Inventario de Licencias y Periféricos', 4, TRUE),                  -- ID 63
    (1, 31, 1, 14, '152405', 'Muebles y Enseres de Oficina', 4, TRUE),                           -- ID 64
    (1, 32, 1, 14, '152805', 'Equipos de Procesamiento de Datos Corporativos', 4, TRUE),         -- ID 65
    (1, 33, 1, 14, '154005', 'Camionetas de Reparto y Logística', 4, TRUE),                      -- ID 66
    (1, 34, 7, 14, '159205', 'Depreciación Acumulada Propiedad, Planta y Equipo', 4, TRUE),      -- ID 67
    (1, 35, 2, 7,  '210510', 'Pagaré Crédito Empresarial Bancolombia LP', 4, TRUE),              -- ID 68
    (1, 36, 2, 15, '220505', 'Proveedores Nacionales de Hardware y Software', 4, TRUE),          -- ID 69
    (1, 37, 2, 15, '233525', 'Honorarios, Arrendamientos y Servicios por Pagar', 4, TRUE),       -- ID 70
    (1, 38, 2, 15, '250505', 'Salarios y Liquidaciones por Pagar', 4, TRUE),                     -- ID 71
    (1, 39, 3, 8,  '310505', 'Capital Autorizado, Suscrito y Pagado', 4, TRUE),                  -- ID 72
    (1, 40, 3, 9,  '330505', 'Reserva Legal Obligatoria (10%)', 4, TRUE),                        -- ID 73
    (1, 41, 3, 10, '360505', 'Utilidad del Ejercicio', 4, TRUE),                                 -- ID 74
    (1, 42, 3, 10, '370505', 'Utilidades Acumuladas de Ejercicios Anteriores', 4, TRUE),         -- ID 75
    (1, 43, 4, 16, '413505', 'Venta de Servidores, Computadores y Redes', 4, TRUE),              -- ID 76
    (1, 44, 4, 16, '415505', 'Servicios de Soporte Técnico e Implementación Cloud', 4, TRUE),    -- ID 77
    (1, 45, 4, 20, '421005', 'Intereses y Rendimientos Financieros CDT y Ahorros', 4, TRUE),     -- ID 78
    (1, 46, 6, 18, '510506', 'Sueldos y Salarios Personal Administrativo', 4, TRUE),             -- ID 79
    (1, 46, 6, 18, '510570', 'Aportes a Seguridad Social, Salud, Pensión y ARL', 4, TRUE),       -- ID 80
    (1, 47, 6, 18, '511010', 'Honorarios Revisoría Fiscal y Asesoría Legal', 4, TRUE),           -- ID 81
    (1, 48, 6, 18, '512010', 'Arrendamiento Sede Principal y Bodega Autopista Norte', 4, TRUE),  -- ID 82
    (1, 49, 6, 18, '513530', 'Energía Eléctrica, Acueducto y Fibra Óptica Dedicada', 4, TRUE),   -- ID 83
    (1, 50, 6, 18, '514515', 'Mantenimiento de Equipos e Instalaciones', 4, TRUE),               -- ID 84
    (1, 51, 6, 18, '516015', 'Gasto Depreciación Propiedad, Planta y Equipo', 4, TRUE),          -- ID 85
    (1, 52, 6, 19, '520506', 'Sueldos y Comisiones Ejecutivos Comerciales', 4, TRUE),            -- ID 86
    (1, 53, 6, 19, '523560', 'Campañas de Marketing Digital y Eventos Corporativos', 4, TRUE),   -- ID 87
    (1, 54, 6, 21, '530505', 'Gastos Bancarios, GMF (4x1000) y Comisiones', 4, TRUE),            -- ID 88
    (1, 54, 6, 21, '530520', 'Intereses de Obligaciones Financieras', 4, TRUE),                  -- ID 89
    (1, 55, 5, 17, '613505', 'Costo de Venta de Hardware y Licencias', 4, TRUE);                 -- ID 90

-- ============================================================================
-- 8. PLAN_CUENTA — EMPRESA 2: Soluciones Clínicas El Bosque Ltda. (IDs 91..104)
-- ============================================================================
INSERT INTO plan_cuenta (id_empresa, id_cuenta_padre, id_tipo_cuenta, id_rubro, codigo, nombre, nivel, acepta_movimiento) VALUES
    (2, NULL, 1, 1,  '1', 'Activo', 1, FALSE),                                                   -- ID 91
    (2, NULL, 2, 2,  '2', 'Pasivo', 1, FALSE),                                                   -- ID 92
    (2, NULL, 3, 3,  '3', 'Patrimonio', 1, FALSE),                                               -- ID 93
    (2, NULL, 4, 16, '4', 'Ingresos', 1, FALSE),                                                 -- ID 94
    (2, NULL, 6, 18, '5', 'Gastos', 1, FALSE),                                                   -- ID 95
    (2, NULL, 5, 17, '6', 'Costos de Servicios Médicos', 1, FALSE),                              -- ID 96
    (2, 91,   1, 11, '111005', 'Banco Davivienda Cuenta Empresarial Clínica', 2, TRUE),          -- ID 97
    (2, 91,   1, 12, '130505', 'EPS y Aseguradoras por Cobrar', 2, TRUE),                        -- ID 98
    (2, 91,   1, 13, '143505', 'Inventario de Insumos Médicos y Quirúrgicos', 2, TRUE),          -- ID 99
    (2, 92,   2, 15, '220505', 'Proveedores de Reactivos y Dispositivos Médicos', 2, TRUE),      -- ID 100
    (2, 93,   3, 8,  '310505', 'Aportes Sociales Socios Clínica El Bosque', 2, TRUE),            -- ID 101
    (2, 93,   3, 10, '360505', 'Utilidad del Ejercicio Clínico', 2, TRUE),                       -- ID 102
    (2, 94,   4, 16, '415510', 'Ingresos por Consulta Especializada y Laboratorio', 2, TRUE),    -- ID 103
    (2, 95,   6, 18, '510506', 'Honorarios y Nómina Personal Médico y Enfermería', 2, TRUE),     -- ID 104
    (2, 96,   5, 17, '613510', 'Costo de Insumos y Reactivos Consumidos', 2, TRUE);              -- ID 105

-- ============================================================================
-- 9. PLAN_CUENTA — EMPRESA 3: Agroindustria Cafetera del Quindío S.A. (IDs 106..113)
-- ============================================================================
INSERT INTO plan_cuenta (id_empresa, id_cuenta_padre, id_tipo_cuenta, id_rubro, codigo, nombre, nivel, acepta_movimiento) VALUES
    (3, NULL, 1, 11, '111005', 'Banco Agrario de Colombia - Cuenta Corriente', 1, TRUE),         -- ID 106
    (3, NULL, 1, 13, '143505', 'Inventario de Café Pergamino y Tostado', 1, TRUE),               -- ID 107
    (3, NULL, 2, 15, '220505', 'Proveedores Agrícolas y Cooperativas Cafeteras', 1, TRUE),       -- ID 108
    (3, NULL, 3, 8,  '310505', 'Capital Accionario Agroindustria Quindío', 1, TRUE),             -- ID 109
    (3, NULL, 3, 10, '360505', 'Utilidad del Ejercicio Agroindustrial', 1, TRUE),                -- ID 110
    (3, NULL, 4, 16, '413510', 'Ventas de Café Especial de Exportación y Nacional', 1, TRUE),    -- ID 111
    (3, NULL, 6, 18, '510506', 'Gastos Operativos de Beneficio y Trilla', 1, TRUE),              -- ID 112
    (3, NULL, 5, 17, '613515', 'Costo de Cosecha y Compra de Grano', 1, TRUE);                   -- ID 113

-- ============================================================================
-- 10. TERCERO (30 Terceros distribuidos en las empresas, IDs 1..30)
-- ============================================================================
INSERT INTO tercero (id_empresa, documento, nombre, tipo) VALUES
    -- Empresa 1 (IDs 1..18)
    (1, '860002964-4', 'Bancolombia S.A.', 'OTRO'),                                              -- ID 1
    (1, '860003020-1', 'Banco de Bogotá S.A.', 'OTRO'),                                          -- ID 2
    (1, '860034313-7', 'Banco Davivienda S.A.', 'OTRO'),                                         -- ID 3
    (1, '900334512-1', 'Importadora Mayorista Andina de Tecnología S.A.S.', 'PROVEEDOR'),        -- ID 4
    (1, '800198432-5', 'Ingram Micro Colombia S.A.S.', 'PROVEEDOR'),                             -- ID 5
    (1, '830054891-2', 'Inmobiliaria Empresarial Parque Norte S.A.', 'PROVEEDOR'),               -- ID 6
    (1, '899999068-1', 'Enel Colombia S.A. E.S.P.', 'PROVEEDOR'),                                -- ID 7
    (1, '830114921-9', 'Colombia Telecomunicaciones S.A. E.S.P. (Movistar Empresas)', 'PROVEEDOR'), -- ID 8
    (1, '900412789-0', 'Audifiscal & Consultores Tributarios S.A.S.', 'PROVEEDOR'),              -- ID 9
    (1, '901122334-8', 'Agencia Digital Growth Marketing S.A.S.', 'PROVEEDOR'),                  -- ID 10
    (1, '860013779-5', 'Universidad El Bosque', 'CLIENTE'),                                      -- ID 11
    (1, '860025900-2', 'Fundación Santa Fe de Bogotá', 'CLIENTE'),                               -- ID 12
    (1, '900512890-8', 'Grupo Logístico Tequendama S.A.S.', 'CLIENTE'),                          -- ID 13
    (1, '800245781-3', 'Almacenes Éxito S.A.', 'CLIENTE'),                                       -- ID 14
    (1, '900765432-1', 'FinTech Pagos Digitales de Colombia S.A.S.', 'CLIENTE'),                 -- ID 15
    (1, '890903938-8', 'Cámara de Comercio de Bogotá', 'CLIENTE'),                               -- ID 16
    (1, '1020789456',  'Carlos Andrés Gómez Restrepo (Gerente Administrativo)', 'OTRO'),         -- ID 17
    (1, '800088702-2', 'EPS Sanitas / Protección Fondo de Pensiones y ARL Sura', 'OTRO'),        -- ID 18
    -- Empresa 2 (IDs 19..25)
    (2, '860034313-7', 'Banco Davivienda S.A.', 'OTRO'),                                         -- ID 19
    (2, '800251440-6', 'EPS Sanitas S.A.S.', 'CLIENTE'),                                         -- ID 20
    (2, '860009578-6', 'Seguros de Vida Suramericana S.A.', 'CLIENTE'),                          -- ID 21
    (2, '830012345-9', 'Rochem Biocare Colombia S.A.S.', 'PROVEEDOR'),                           -- ID 22
    (2, '900223344-5', 'Distribuidora Médica Quirúrgica de la Sabana Ltda.', 'PROVEEDOR'),       -- ID 23
    (2, '52890123',    'Dra. María Fernanda Ospina Vargas (Directora Médica)', 'OTRO'),          -- ID 24
    (2, '1018456789',  'Camilo Ernesto Rojas Pérez (Jefe de Laboratorio)', 'OTRO'),              -- ID 25
    -- Empresa 3 (IDs 26..30)
    (3, '800037800-8', 'Banco Agrario de Colombia S.A.', 'OTRO'),                                -- ID 26
    (3, '890001234-5', 'Cooperativa de Caficultores del Quindío', 'PROVEEDOR'),                  -- ID 27
    (3, '900887766-1', 'Exportadora Nacional de Cafés Especiales S.A.S.', 'CLIENTE'),            -- ID 28
    (3, '800998877-2', 'Tostadora Gourmet de la Sabana S.A.', 'CLIENTE'),                        -- ID 29
    (3, '75098123',    'Jorge Eliécer Vallejo Mejía (Jefe de Planta y Trilla)', 'OTRO');         -- ID 30

-- ============================================================================
-- 11. CENTRO_COSTO (15 Centros de Costo, IDs 1..15)
-- ============================================================================
INSERT INTO centro_costo (id_empresa, codigo, nombre) VALUES
    -- Empresa 1 (IDs 1..6)
    (1, 'CC-ADM-01', 'Gerencia General, Finanzas y Contabilidad'),                               -- ID 1
    (1, 'CC-ADM-02', 'Talento Humano y Servicios Generales'),                                    -- ID 2
    (1, 'CC-COM-01', 'Ventas Corporativas y Licitaciones'),                                      -- ID 3
    (1, 'CC-COM-02', 'Marketing Digital y Canal E-Commerce'),                                    -- ID 4
    (1, 'CC-LOG-01', 'Bodega Central e Inventarios Autopista Norte'),                            -- ID 5
    (1, 'CC-TEC-01', 'Ingeniería, Soporte Técnico y Cloud'),                                     -- ID 6
    -- Empresa 2 (IDs 7..10)
    (2, 'CC-CLI-URG', 'Unidad de Consulta Externa y Urgencias'),                                 -- ID 7
    (2, 'CC-CLI-LAB', 'Laboratorio Clínico y Diagnóstico Biomédico'),                            -- ID 8
    (2, 'CC-CLI-CIR', 'Salas de Procedimientos Ambulatorios'),                                   -- ID 9
    (2, 'CC-CLI-ADM', 'Facturación Médica y Administración Clínica'),                            -- ID 10
    -- Empresa 3 (IDs 11..13)
    (3, 'CC-AGR-TRI', 'Planta de Trilla, Tostión y Empaque Armenia'),                            -- ID 11
    (3, 'CC-AGR-EXP', 'Comercialización y Logística de Exportación'),                            -- ID 12
    (3, 'CC-AGR-ADM', 'Administración Central Quindío'),                                         -- ID 13
    -- Empresa 4 (IDs 14..15)
    (4, 'CC-CON-DEV', 'Fábrica de Software y Arquitectura Cloud'),                               -- ID 14
    (4, 'CC-CON-ADM', 'Dirección Corporativa Regional');                                         -- ID 15

-- ============================================================================
-- 12. ASIENTOS Y MOVIMIENTOS — EMPRESA 1 · PERIODO 1 (2024, CERRADO)
-- ============================================================================

-- Asiento 1 (ID 1): Constitución de la sociedad en 2024 ($200,000,000)
INSERT INTO asiento (id_periodo, id_tipo_asiento, numero, fecha, descripcion, estado) VALUES
    (1, 1, 1, '2024-01-05', 'Asiento de apertura por escritura pública de constitución y pago de capital suscrito', 'CONTABILIZADO');

INSERT INTO movimiento (id_asiento, id_cuenta, id_tercero, id_centro_costo, debe, haber) VALUES
    (1, 58, 2,    1, 130000000.00, 0.00),         -- Debe: Banco de Bogotá (111005)
    (1, 59, 1,    1, 40000000.00,  0.00),         -- Debe: Bancolombia Ahorros (111010)
    (1, 64, NULL, 1, 12000000.00,  0.00),         -- Debe: Muebles y Enseres (152405)
    (1, 65, NULL, 6, 18000000.00,  0.00),         -- Debe: Equipos de Cómputo (152805)
    (1, 72, NULL, 1, 0.00,         200000000.00); -- Haber: Capital Suscrito y Pagado (310505)

-- Asiento 2 (ID 2): Compras de inventario en 2024 ($95,000,000)
INSERT INTO asiento (id_periodo, id_tipo_asiento, numero, fecha, descripcion, estado) VALUES
    (1, 2, 2, '2024-03-18', 'Compra de lote inicial de servidores y switches empresariales a Ingram Micro', 'CONTABILIZADO');

INSERT INTO movimiento (id_asiento, id_cuenta, id_tercero, id_centro_costo, debe, haber) VALUES
    (2, 62, 5, 5, 95000000.00, 0.00),             -- Debe: Inventario Servidores (143505)
    (2, 58, 2, 5, 0.00,        95000000.00);      -- Haber: Banco de Bogotá (111005)

-- Asiento 3 (ID 3): Ventas de hardware y soporte 2024 ($140,000,000) y costo de venta ($75,000,000)
INSERT INTO asiento (id_periodo, id_tipo_asiento, numero, fecha, descripcion, estado) VALUES
    (1, 2, 3, '2024-07-22', 'Facturación consolidada de equipamiento y contratos de soporte 2024 a Universidad El Bosque', 'CONTABILIZADO');

INSERT INTO movimiento (id_asiento, id_cuenta, id_tercero, id_centro_costo, debe, haber) VALUES
    (3, 58, 11, 3, 140000000.00, 0.00),           -- Debe: Banco de Bogotá (111005)
    (3, 76, 11, 3, 0.00,         115000000.00),   -- Haber: Venta de Servidores (413505)
    (3, 77, 11, 6, 0.00,         25000000.00),    -- Haber: Servicios de Soporte Cloud (415505)
    (3, 90, 11, 5, 75000000.00,  0.00),           -- Debe: Costo de Venta Hardware (613505)
    (3, 62, 11, 5, 0.00,         75000000.00);    -- Haber: Inventario Servidores (143505)

-- Asiento 4 (ID 4): Gastos operacionales de administración y ventas 2024 ($35,000,000)
INSERT INTO asiento (id_periodo, id_tipo_asiento, numero, fecha, descripcion, estado) VALUES
    (1, 2, 4, '2024-11-15', 'Pago de nómina administrativa, arrendamientos y servicios públicos ejercicio 2024', 'CONTABILIZADO');

INSERT INTO movimiento (id_asiento, id_cuenta, id_tercero, id_centro_costo, debe, haber) VALUES
    (4, 79, 17, 1, 20000000.00, 0.00),            -- Debe: Sueldos Administrativos (510506)
    (4, 82, 6,  1, 10000000.00, 0.00),            -- Debe: Arrendamiento Sede (512010)
    (4, 83, 7,  1, 5000000.00,  0.00),            -- Debe: Servicios Públicos (513530)
    (4, 58, 2,  1, 0.00,        35000000.00);     -- Haber: Banco de Bogotá (111005)

-- Asiento 5 (ID 5): Cierre del ejercicio 2024 (Utilidad neta = $30,000,000: $3,000,000 a Reserva Legal y $27,000,000 a Utilidades Acumuladas)
INSERT INTO asiento (id_periodo, id_tipo_asiento, numero, fecha, descripcion, estado) VALUES
    (1, 4, 5, '2024-12-31', 'Asiento de cierre contable ejercicio 2024 y apropiación de reserva legal', 'CONTABILIZADO');

INSERT INTO movimiento (id_asiento, id_cuenta, id_tercero, id_centro_costo, debe, haber) VALUES
    (5, 76, NULL, NULL, 115000000.00, 0.00),      -- Cierra Venta de Servidores (413505)
    (5, 77, NULL, NULL, 25000000.00,  0.00),      -- Cierra Servicios de Soporte (415505)
    (5, 90, NULL, NULL, 0.00,         75000000.00), -- Cierra Costo de Ventas (613505)
    (5, 79, NULL, NULL, 0.00,         20000000.00), -- Cierra Sueldos (510506)
    (5, 82, NULL, NULL, 0.00,         10000000.00), -- Cierra Arrendamiento (512010)
    (5, 83, NULL, NULL, 0.00,         5000000.00),  -- Cierra Servicios Públicos (513530)
    (5, 73, NULL, NULL, 0.00,         3000000.00),  -- Reserva Legal 10% (330505)
    (5, 75, NULL, NULL, 0.00,         27000000.00); -- Utilidades Acumuladas (370505)

INSERT INTO cierre_periodo (id_periodo, id_asiento_cierre, utilidad_neta, fecha_cierre) VALUES
    (1, 5, 30000000.00, '2024-12-31 23:55:00-05');

-- ============================================================================
-- 13. ASIENTOS Y MOVIMIENTOS — EMPRESA 1 · PERIODO 2 (2025, CERRADO)
-- ============================================================================

-- Asiento 1 de 2025 (ID 6): Compra de camioneta de reparto con crédito bancario Bancolombia ($85,000,000)
INSERT INTO asiento (id_periodo, id_tipo_asiento, numero, fecha, descripcion, estado) VALUES
    (2, 2, 1, '2025-02-10', 'Adquisición de camioneta de reparto logística con cuota inicial y pagaré empresarial Bancolombia', 'CONTABILIZADO');

INSERT INTO movimiento (id_asiento, id_cuenta, id_tercero, id_centro_costo, debe, haber) VALUES
    (6, 66, 1, 5, 85000000.00, 0.00),             -- Debe: Flota y Equipo de Transporte (154005)
    (6, 58, 2, 5, 0.00,        25000000.00),      -- Haber: Banco de Bogotá cuota inicial (111005)
    (6, 68, 1, 5, 0.00,        60000000.00);      -- Haber: Pagaré Bancolombia LP (210510)

-- Asiento 2 de 2025 (ID 7): Compra de inventario de servidores y licencias ($130,000,000)
INSERT INTO asiento (id_periodo, id_tipo_asiento, numero, fecha, descripcion, estado) VALUES
    (2, 2, 2, '2025-04-12', 'Compra de inventario de servidores y licencias corporativas a Importadora Mayorista Andina', 'CONTABILIZADO');

INSERT INTO movimiento (id_asiento, id_cuenta, id_tercero, id_centro_costo, debe, haber) VALUES
    (7, 62, 4, 5, 90000000.00, 0.00),             -- Debe: Inventario Servidores (143505)
    (7, 63, 4, 5, 40000000.00, 0.00),             -- Debe: Inventario Licencias (143510)
    (7, 58, 2, 5, 0.00,        100000000.00),     -- Haber: Banco de Bogotá (111005)
    (7, 69, 4, 5, 0.00,        30000000.00);      -- Haber: Proveedores Nacionales (220505)

-- Asiento 3 de 2025 (ID 8): Ventas corporativas a Fundación Santa Fe y Almacenes Éxito ($220,000,000) + Costo ($110,000,000)
INSERT INTO asiento (id_periodo, id_tipo_asiento, numero, fecha, descripcion, estado) VALUES
    (2, 2, 3, '2025-08-19', 'Facturación de infraestructura TI y soporte anual a Fundación Santa Fe y Almacenes Éxito', 'CONTABILIZADO');

INSERT INTO movimiento (id_asiento, id_cuenta, id_tercero, id_centro_costo, debe, haber) VALUES
    (8, 58, 12, 3, 150000000.00, 0.00),           -- Debe: Banco de Bogotá (111005)
    (8, 59, 14, 3, 50000000.00,  0.00),           -- Debe: Bancolombia Ahorros (111010)
    (8, 61, 14, 3, 20000000.00,  0.00),           -- Debe: Clientes Corporativos (130505)
    (8, 76, 12, 3, 0.00,         175000000.00),   -- Haber: Venta de Servidores (413505)
    (8, 77, 14, 6, 0.00,         45000000.00),    -- Haber: Servicios de Soporte Cloud (415505)
    (8, 90, 12, 5, 110000000.00, 0.00),           -- Debe: Costo de Venta Hardware (613505)
    (8, 62, 12, 5, 0.00,         80000000.00),    -- Haber: Inventario Servidores (143505)
    (8, 63, 14, 5, 0.00,         30000000.00);    -- Haber: Inventario Licencias (143510)

-- Asiento 4 de 2025 (ID 9): Gastos de nómina, honorarios, arriendo, marketing e intereses 2025 ($62,000,000)
INSERT INTO asiento (id_periodo, id_tipo_asiento, numero, fecha, descripcion, estado) VALUES
    (2, 2, 4, '2025-10-28', 'Gastos operacionales, seguridad social, revisoría fiscal, mercadeo e intereses bancarios 2025', 'CONTABILIZADO');

INSERT INTO movimiento (id_asiento, id_cuenta, id_tercero, id_centro_costo, debe, haber) VALUES
    (9, 79, 17, 1, 24000000.00, 0.00),            -- Debe: Sueldos Administrativos (510506)
    (9, 80, 18, 2, 7000000.00,  0.00),            -- Debe: Aportes Seguridad Social (510570)
    (9, 81, 9,  1, 6000000.00,  0.00),            -- Debe: Honorarios Revisoría Fiscal (511010)
    (9, 82, 6,  1, 12000000.00, 0.00),            -- Debe: Arrendamiento Sede (512010)
    (9, 86, 17, 3, 8000000.00,  0.00),            -- Debe: Sueldos y Comisiones Ventas (520506)
    (9, 89, 1,  1, 5000000.00,  0.00),            -- Debe: Intereses Obligaciones Financieras (530520)
    (9, 58, 2,  1, 0.00,        62000000.00);     -- Haber: Banco de Bogotá (111005)

-- Asiento 5 de 2025 (ID 10): Ajuste por depreciación anual 2025 ($8,000,000)
INSERT INTO asiento (id_periodo, id_tipo_asiento, numero, fecha, descripcion, estado) VALUES
    (2, 3, 5, '2025-12-30', 'Ajuste por depreciación anual de muebles, equipos de cómputo y flota de transporte 2025', 'CONTABILIZADO');

INSERT INTO movimiento (id_asiento, id_cuenta, id_tercero, id_centro_costo, debe, haber) VALUES
    (10, 85, NULL, 1, 8000000.00, 0.00),          -- Debe: Gasto Depreciación PPE (516015)
    (10, 67, NULL, 1, 0.00,       8000000.00);    -- Haber: Depreciación Acumulada PPE (159205)

-- Asiento 6 de 2025 (ID 11): Cierre del ejercicio 2025 (Utilidad neta = $40,000,000 trasladada a 360505)
INSERT INTO asiento (id_periodo, id_tipo_asiento, numero, fecha, descripcion, estado) VALUES
    (2, 4, 6, '2025-12-31', 'Asiento de cierre contable del ejercicio 2025 y traslado de utilidad neta al patrimonio', 'CONTABILIZADO');

INSERT INTO movimiento (id_asiento, id_cuenta, id_tercero, id_centro_costo, debe, haber) VALUES
    (11, 76, NULL, NULL, 175000000.00, 0.00),     -- Cierra Venta de Servidores (413505)
    (11, 77, NULL, NULL, 45000000.00,  0.00),     -- Cierra Servicios de Soporte (415505)
    (11, 90, NULL, NULL, 0.00,         110000000.00), -- Cierra Costo de Ventas (613505)
    (11, 79, NULL, NULL, 0.00,         24000000.00),  -- Cierra Sueldos Adm (510506)
    (11, 80, NULL, NULL, 0.00,         7000000.00),   -- Cierra Seguridad Social (510570)
    (11, 81, NULL, NULL, 0.00,         6000000.00),   -- Cierra Honorarios (511010)
    (11, 82, NULL, NULL, 0.00,         12000000.00),  -- Cierra Arrendamiento (512010)
    (11, 85, NULL, NULL, 0.00,         8000000.00),   -- Cierra Depreciación (516015)
    (11, 86, NULL, NULL, 0.00,         8000000.00),   -- Cierra Comisiones Ventas (520506)
    (11, 89, NULL, NULL, 0.00,         5000000.00),   -- Cierra Intereses (530520)
    (11, 74, NULL, NULL, 0.00,         40000000.00);  -- Traslada Utilidad a 360505

INSERT INTO cierre_periodo (id_periodo, id_asiento_cierre, utilidad_neta, fecha_cierre) VALUES
    (2, 11, 40000000.00, '2025-12-31 23:58:00-05');

-- ============================================================================
-- 14. ASIENTOS Y MOVIMIENTOS — EMPRESA 1 · PERIODO 3 (2026, ABIERTO — 12 ASIENTOS)
-- ============================================================================

-- Asiento 1 de 2026 (ID 12): Apertura de CDT en Banco Davivienda ($50,000,000) y fondeo de Caja General ($5,000,000) y Caja Menor ($2,000,000)
INSERT INTO asiento (id_periodo, id_tipo_asiento, numero, fecha, descripcion, estado) VALUES
    (3, 2, 1, '2026-01-12', 'Constitución de CDT corporativo a 90 días en Davivienda y apertura de fondos de caja', 'CONTABILIZADO');

INSERT INTO movimiento (id_asiento, id_cuenta, id_tercero, id_centro_costo, debe, haber) VALUES
    (12, 60, 3, 1, 50000000.00, 0.00),            -- Debe: CDT Davivienda (122505)
    (12, 56, 2, 1, 5000000.00,  0.00),            -- Debe: Caja General Bogotá (110505)
    (12, 57, 2, 2, 2000000.00,  0.00),            -- Debe: Caja Menor Administración (110510)
    (12, 58, 2, 1, 0.00,        57000000.00);     -- Haber: Banco de Bogotá (111005)

-- Asiento 2 de 2026 (ID 13): Compra de servidores y licencias a Ingram Micro e Importadora Andina ($145,000,000)
INSERT INTO asiento (id_periodo, id_tipo_asiento, numero, fecha, descripcion, estado) VALUES
    (3, 2, 2, '2026-02-05', 'Compra de servidores rack y licencias anuales según facturas FC-8810 y FC-8815', 'CONTABILIZADO');

INSERT INTO movimiento (id_asiento, id_cuenta, id_tercero, id_centro_costo, debe, haber) VALUES
    (13, 62, 5, 5, 105000000.00, 0.00),           -- Debe: Inventario Servidores (143505)
    (13, 63, 4, 5, 40000000.00,  0.00),           -- Debe: Inventario Licencias (143510)
    (13, 58, 5, 5, 0.00,         65000000.00),    -- Haber: Banco de Bogotá (111005)
    (13, 69, 4, 5, 0.00,         80000000.00);    -- Haber: Proveedores Nacionales (220505)

-- Asiento 3 de 2026 (ID 14): Venta de centro de datos a Universidad El Bosque ($128,000,000) + Costo ($64,000,000)
INSERT INTO asiento (id_periodo, id_tipo_asiento, numero, fecha, descripcion, estado) VALUES
    (3, 2, 3, '2026-03-10', 'Venta e implementación de clúster de servidores para laboratorios Universidad El Bosque FV-2026-001', 'CONTABILIZADO');

INSERT INTO movimiento (id_asiento, id_cuenta, id_tercero, id_centro_costo, debe, haber) VALUES
    (14, 58, 11, 3, 90000000.00,  0.00),          -- Debe: Banco de Bogotá (111005)
    (14, 61, 11, 3, 38000000.00,  0.00),          -- Debe: Clientes Corporativos (130505)
    (14, 76, 11, 3, 0.00,         100000000.00),  -- Haber: Venta de Servidores (413505)
    (14, 77, 11, 6, 0.00,         28000000.00),   -- Haber: Servicios Soporte Cloud (415505)
    (14, 90, 11, 5, 64000000.00,  0.00),          -- Debe: Costo de Venta Hardware (613505)
    (14, 62, 11, 5, 0.00,         52000000.00),   -- Haber: Inventario Servidores (143505)
    (14, 63, 11, 5, 0.00,         12000000.00);   -- Haber: Inventario Licencias (143510)

-- Asiento 4 de 2026 (ID 15): Recaudo de cartera Almacenes Éxito y pago a proveedores de hardware
INSERT INTO asiento (id_periodo, id_tipo_asiento, numero, fecha, descripcion, estado) VALUES
    (3, 2, 4, '2026-04-08', 'Recaudo de factura pendiente de Almacenes Éxito y abono a proveedores nacionales', 'CONTABILIZADO');

INSERT INTO movimiento (id_asiento, id_cuenta, id_tercero, id_centro_costo, debe, haber) VALUES
    (15, 59, 14, 3, 20000000.00, 0.00),           -- Debe: Bancolombia Ahorros (111010)
    (15, 61, 14, 3, 0.00,        20000000.00),    -- Haber: Clientes Corporativos (130505)
    (15, 69, 4,  5, 55000000.00, 0.00),           -- Debe: Proveedores Nacionales (220505)
    (15, 58, 2,  5, 0.00,        55000000.00);    -- Haber: Banco de Bogotá (111005)

-- Asiento 5 de 2026 (ID 16): Venta de infraestructura Cloud a FinTech Pagos Digitales y Cámara de Comercio ($152,000,000) + Costo ($71,000,000)
INSERT INTO asiento (id_periodo, id_tipo_asiento, numero, fecha, descripcion, estado) VALUES
    (3, 2, 5, '2026-05-19', 'Facturación de licenciamiento corporativo y nodos de red a FinTech Pagos y Cámara de Comercio FV-2026-002', 'CONTABILIZADO');

INSERT INTO movimiento (id_asiento, id_cuenta, id_tercero, id_centro_costo, debe, haber) VALUES
    (16, 58, 15, 3, 112000000.00, 0.00),          -- Debe: Banco de Bogotá (111005)
    (16, 61, 16, 3, 40000000.00,  0.00),          -- Debe: Clientes Corporativos (130505)
    (16, 76, 15, 3, 0.00,         110000000.00),  -- Haber: Venta de Servidores (413505)
    (16, 77, 16, 6, 0.00,         42000000.00),   -- Haber: Servicios Soporte Cloud (415505)
    (16, 90, 15, 5, 71000000.00,  0.00),          -- Debe: Costo de Venta Hardware (613505)
    (16, 62, 15, 5, 0.00,         46000000.00),   -- Haber: Inventario Servidores (143505)
    (16, 63, 16, 5, 0.00,         25000000.00);   -- Haber: Inventario Licencias (143510)

-- Asiento 6 de 2026 (ID 17): Nómina primer semestre 2026 y seguridad social ($49,500,000)
INSERT INTO asiento (id_periodo, id_tipo_asiento, numero, fecha, descripcion, estado) VALUES
    (3, 2, 6, '2026-06-25', 'Causación y pago de nómina administrativa, comercial y seguridad social primer semestre 2026', 'CONTABILIZADO');

INSERT INTO movimiento (id_asiento, id_cuenta, id_tercero, id_centro_costo, debe, haber) VALUES
    (17, 79, 17, 1, 22000000.00, 0.00),           -- Debe: Sueldos Administrativos (510506)
    (17, 80, 18, 2, 8500000.00,  0.00),           -- Debe: Aportes Seguridad Social (510570)
    (17, 86, 17, 3, 19000000.00, 0.00),           -- Debe: Sueldos y Comisiones Ventas (520506)
    (17, 58, 2,  1, 0.00,        44500000.00),    -- Haber: Banco de Bogotá (111005)
    (17, 71, 17, 2, 0.00,        5000000.00);     -- Haber: Salarios y Liquidaciones por Pagar (250505)

-- Asiento 7 de 2026 (ID 18): Arrendamientos, servicios públicos, mantenimiento, honorarios y pauta digital ($36,800,000)
INSERT INTO asiento (id_periodo, id_tipo_asiento, numero, fecha, descripcion, estado) VALUES
    (3, 2, 7, '2026-07-18', 'Registro de gastos de arrendamiento de bodega, energía, fibra óptica, auditoría y marketing digital', 'CONTABILIZADO');

INSERT INTO movimiento (id_asiento, id_cuenta, id_tercero, id_centro_costo, debe, haber) VALUES
    (18, 82, 6,  1, 14000000.00, 0.00),           -- Debe: Arrendamiento Sede y Bodega (512010)
    (18, 83, 7,  1, 4200000.00,  0.00),           -- Debe: Energía y Fibra Óptica (513530)
    (18, 84, 8,  6, 3600000.00,  0.00),           -- Debe: Mantenimiento Equipos (514515)
    (18, 81, 9,  1, 5500000.00,  0.00),           -- Debe: Honorarios Revisoría Fiscal (511010)
    (18, 87, 10, 4, 9500000.00,  0.00),           -- Debe: Campañas Marketing Digital (523560)
    (18, 58, 2,  1, 0.00,        30000000.00),    -- Haber: Banco de Bogotá (111005)
    (18, 70, 9,  1, 0.00,        6800000.00);     -- Haber: Costos y Gastos por Pagar (233525)

-- Asiento 8 de 2026 (ID 19): Amortización de pagaré Bancolombia ($15,000,000 capital + $3,800,000 intereses + $700,000 GMF)
INSERT INTO asiento (id_periodo, id_tipo_asiento, numero, fecha, descripcion, estado) VALUES
    (3, 2, 8, '2026-08-14', 'Abono a capital e intereses de obligación financiera pagaré Bancolombia y cargo por GMF 4x1000', 'CONTABILIZADO');

INSERT INTO movimiento (id_asiento, id_cuenta, id_tercero, id_centro_costo, debe, haber) VALUES
    (19, 68, 1, 1, 15000000.00, 0.00),            -- Debe: Pagaré Bancolombia LP (210510)
    (19, 89, 1, 1, 3800000.00,  0.00),            -- Debe: Intereses Obligaciones Financieras (530520)
    (19, 88, 1, 1, 700000.00,   0.00),            -- Debe: Gastos Bancarios y GMF (530505)
    (19, 59, 1, 1, 0.00,        19500000.00);     -- Haber: Bancolombia Ahorros (111010)

-- Asiento 9 de 2026 (ID 20): Ajuste por depreciación acumulada 2026 ($6,500,000) y rendimientos del CDT Davivienda ($2,400,000)
INSERT INTO asiento (id_periodo, id_tipo_asiento, numero, fecha, descripcion, estado) VALUES
    (3, 3, 9, '2026-09-30', 'Ajuste por depreciación de propiedad, planta y equipo y causación de rendimientos CDT Davivienda', 'CONTABILIZADO');

INSERT INTO movimiento (id_asiento, id_cuenta, id_tercero, id_centro_costo, debe, haber) VALUES
    (20, 85, NULL, 1, 6500000.00, 0.00),          -- Debe: Gasto Depreciación PPE (516015)
    (20, 67, NULL, 1, 0.00,       6500000.00),    -- Haber: Depreciación Acumulada PPE (159205)
    (20, 59, 3,    1, 2400000.00, 0.00),          -- Debe: Bancolombia Ahorros (111010)
    (20, 78, 3,    1, 0.00,       2400000.00);    -- Haber: Rendimientos Financieros CDT (421005)

-- Asiento 10 de 2026 (ID 21): Venta de proyecto de nube híbrida a Grupo Logístico Tequendama ($65,000,000) + Costo ($15,000,000)
INSERT INTO asiento (id_periodo, id_tipo_asiento, numero, fecha, descripcion, estado) VALUES
    (3, 2, 10, '2026-10-15', 'Facturación de proyecto de nube híbrida y equipamiento a Grupo Logístico Tequendama FV-2026-003', 'CONTABILIZADO');

INSERT INTO movimiento (id_asiento, id_cuenta, id_tercero, id_centro_costo, debe, haber) VALUES
    (21, 58, 13, 3, 45000000.00, 0.00),           -- Debe: Banco de Bogotá (111005)
    (21, 61, 13, 3, 20000000.00, 0.00),           -- Debe: Clientes Corporativos (130505)
    (21, 76, 13, 3, 0.00,        30000000.00),    -- Haber: Venta de Servidores (413505)
    (21, 77, 13, 6, 0.00,        35000000.00),    -- Haber: Servicios Soporte Cloud (415505)
    (21, 90, 13, 5, 15000000.00, 0.00),           -- Debe: Costo de Venta Hardware (613505)
    (21, 62, 13, 5, 0.00,        10000000.00),    -- Haber: Inventario Servidores (143505)
    (21, 63, 13, 5, 0.00,        5000000.00);     -- Haber: Inventario Licencias (143510)

-- Asiento 11 de 2026 (ID 22): EN BORRADOR — Recaudo de cartera Universidad El Bosque ($18,000,000) listo para contabilizar
INSERT INTO asiento (id_periodo, id_tipo_asiento, numero, fecha, descripcion, estado) VALUES
    (3, 2, 11, '2026-10-25', 'Recaudo parcial de cartera Universidad El Bosque por transferencia bancaria (en borrador)', 'BORRADOR');

INSERT INTO movimiento (id_asiento, id_cuenta, id_tercero, id_centro_costo, debe, haber) VALUES
    (22, 58, 11, 3, 18000000.00, 0.00),           -- Debe: Banco de Bogotá (111005)
    (22, 61, 11, 3, 0.00,        18000000.00);    -- Haber: Clientes Corporativos (130505)

-- Asiento 12 de 2026 (ID 23): EN BORRADOR — Compra de papelería y elementos de cafetería por Caja Menor ($850,000)
INSERT INTO asiento (id_periodo, id_tipo_asiento, numero, fecha, descripcion, estado) VALUES
    (3, 2, 12, '2026-10-28', 'Reembolso de caja menor por mantenimiento locativo menor (en borrador)', 'BORRADOR');

INSERT INTO movimiento (id_asiento, id_cuenta, id_tercero, id_centro_costo, debe, haber) VALUES
    (23, 84, 6, 2, 850000.00, 0.00),              -- Debe: Mantenimiento de Equipos e Instalaciones (514515)
    (23, 57, 2, 2, 0.00,      850000.00);         -- Haber: Caja Menor Administración (110510)

-- ============================================================================
-- 15. ASIENTOS Y MOVIMIENTOS — EMPRESA 2: Soluciones Clínicas El Bosque Ltda.
-- ============================================================================

-- Periodo 4 (2025, CERRADO) — Asiento 1 (ID 24): Apertura Clínica El Bosque ($150,000,000)
INSERT INTO asiento (id_periodo, id_tipo_asiento, numero, fecha, descripcion, estado) VALUES
    (4, 1, 1, '2025-01-10', 'Aporte social inicial de socios para dotación de laboratorio y consultorios', 'CONTABILIZADO');

INSERT INTO movimiento (id_asiento, id_cuenta, id_tercero, id_centro_costo, debe, haber) VALUES
    (24, 97,  19,   10, 120000000.00, 0.00),      -- Debe: Banco Davivienda Clínica (111005)
    (24, 99,  22,   8,  30000000.00,  0.00),      -- Debe: Inventario Insumos Médicos (143505)
    (24, 101, NULL, 10, 0.00,         150000000.00); -- Haber: Aportes Sociales (310505)

-- Periodo 4 (2025, CERRADO) — Asiento 2 (ID 25): Ingresos por convenios EPS ($95,000,000), costos ($20,000,000) y nómina médica ($45,000,000)
INSERT INTO asiento (id_periodo, id_tipo_asiento, numero, fecha, descripcion, estado) VALUES
    (4, 2, 2, '2025-08-15', 'Facturación de servicios médicos y laboratorio a EPS Sanitas y Sura 2025', 'CONTABILIZADO');

INSERT INTO movimiento (id_asiento, id_cuenta, id_tercero, id_centro_costo, debe, haber) VALUES
    (25, 97,  20, 7, 50000000.00, 0.00),          -- Debe: Banco Davivienda Clínica (111005)
    (25, 98,  20, 7, 45000000.00, 0.00),          -- Debe: EPS por Cobrar (130505)
    (25, 103, 20, 7, 0.00,        95000000.00),   -- Haber: Ingresos Consulta y Laboratorio (415510)
    (25, 105, 22, 8, 20000000.00, 0.00),          -- Debe: Costo de Insumos Consumidos (613510)
    (25, 99,  22, 8, 0.00,        20000000.00),   -- Haber: Inventario Insumos Médicos (143505)
    (25, 104, 24, 7, 45000000.00, 0.00),          -- Debe: Honorarios y Nómina Médica (510506)
    (25, 97,  19, 10, 0.00,       45000000.00);   -- Haber: Banco Davivienda Clínica (111005)

-- Periodo 4 (2025, CERRADO) — Asiento 3 (ID 26): Cierre 2025 Clínica El Bosque (Utilidad = $30,000,000)
INSERT INTO asiento (id_periodo, id_tipo_asiento, numero, fecha, descripcion, estado) VALUES
    (4, 4, 3, '2025-12-31', 'Cierre contable ejercicio 2025 Soluciones Clínicas El Bosque Ltda.', 'CONTABILIZADO');

INSERT INTO movimiento (id_asiento, id_cuenta, id_tercero, id_centro_costo, debe, haber) VALUES
    (26, 103, NULL, NULL, 95000000.00, 0.00),     -- Cierra Ingresos Médicos (415510)
    (26, 105, NULL, NULL, 0.00,        20000000.00), -- Cierra Costo Insumos (613510)
    (26, 104, NULL, NULL, 0.00,        45000000.00), -- Cierra Nómina Médica (510506)
    (26, 102, NULL, NULL, 0.00,        30000000.00); -- Traslada Utilidad a 360505

INSERT INTO cierre_periodo (id_periodo, id_asiento_cierre, utilidad_neta, fecha_cierre) VALUES
    (4, 26, 30000000.00, '2025-12-31 23:50:00-05');

-- Periodo 5 (2026-S1, CERRADO) — Asiento 1 (ID 27) y Asiento 2 de Cierre (ID 28)
INSERT INTO asiento (id_periodo, id_tipo_asiento, numero, fecha, descripcion, estado) VALUES
    (5, 2, 1, '2026-04-20', 'Facturación primer semestre 2026 por convenios de diagnóstico clínico', 'CONTABILIZADO'),
    (5, 4, 2, '2026-06-30', 'Cierre contable primer semestre 2026 Soluciones Clínicas El Bosque', 'CONTABILIZADO');

INSERT INTO movimiento (id_asiento, id_cuenta, id_tercero, id_centro_costo, debe, haber) VALUES
    (27, 97,  21,   8,    60000000.00, 0.00),
    (27, 103, 21,   8,    0.00,        60000000.00),
    (27, 104, 25,   8,    25000000.00, 0.00),
    (27, 97,  19,   10,   0.00,        25000000.00),
    (28, 103, NULL, NULL, 60000000.00, 0.00),
    (28, 104, NULL, NULL, 0.00,        25000000.00),
    (28, 102, NULL, NULL, 0.00,        35000000.00);

INSERT INTO cierre_periodo (id_periodo, id_asiento_cierre, utilidad_neta, fecha_cierre) VALUES
    (5, 28, 35000000.00, '2026-06-30 23:55:00-05');

-- Periodo 6 (2026-S2, ABIERTO) — Asiento 1 (ID 29): Compra de reactivos y facturación segundo semestre
INSERT INTO asiento (id_periodo, id_tipo_asiento, numero, fecha, descripcion, estado) VALUES
    (6, 2, 1, '2026-09-10', 'Compra de reactivos a Rochem Biocare y atención de pacientes asegurados S2-2026', 'CONTABILIZADO');

INSERT INTO movimiento (id_asiento, id_cuenta, id_tercero, id_centro_costo, debe, haber) VALUES
    (29, 99,  22, 8, 18000000.00, 0.00),
    (29, 100, 22, 8, 0.00,        18000000.00),
    (29, 97,  20, 7, 48000000.00, 0.00),
    (29, 103, 20, 7, 0.00,        48000000.00),
    (29, 104, 24, 7, 19000000.00, 0.00),
    (29, 97,  19, 10, 0.00,       19000000.00);

-- ============================================================================
-- 16. ASIENTOS Y MOVIMIENTOS — EMPRESA 3: Agroindustria Cafetera del Quindío S.A.
-- ============================================================================

-- Periodo 8 (2026, ABIERTO) — Asientos 1 y 2 (IDs 30 y 31)
INSERT INTO asiento (id_periodo, id_tipo_asiento, numero, fecha, descripcion, estado) VALUES
    (8, 1, 1, '2026-01-15', 'Aporte de capital accionario e inventario inicial de café pergamino seco', 'CONTABILIZADO'),
    (8, 2, 2, '2026-06-18', 'Exportación de lote de café especial a clientes nacionales y registro de costos de trilla', 'CONTABILIZADO');

INSERT INTO movimiento (id_asiento, id_cuenta, id_tercero, id_centro_costo, debe, haber) VALUES
    (30, 106, 26,   13, 90000000.00,  0.00),
    (30, 107, 27,   11, 50000000.00,  0.00),
    (30, 109, NULL, 13, 0.00,         140000000.00),
    (31, 106, 28,   12, 110000000.00, 0.00),
    (31, 111, 28,   12, 0.00,         110000000.00),
    (31, 113, 27,   11, 45000000.00,  0.00),
    (31, 107, 27,   11, 0.00,         45000000.00),
    (31, 112, 30,   11, 16000000.00,  0.00),
    (31, 106, 26,   13, 0.00,         16000000.00);

-- ============================================================================
-- 17. CIERRES SIN MOVIMIENTOS — Periodos 7 y 9 (2025, CERRADOS)
-- ============================================================================
-- Ambos periodos se cerraron sin asientos: utilidad cero y sin asiento de cierre.
INSERT INTO cierre_periodo (id_periodo, id_asiento_cierre, utilidad_neta, fecha_cierre) VALUES
    (7, NULL, 0.00, '2025-12-31 23:59:00-05'),
    (9, NULL, 0.00, '2025-12-31 23:59:00-05');

COMMIT;
