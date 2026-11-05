-- =============================================================================
-- 05_verificacion.sql
-- Scripts varios: comprobaciones de estructura y de las reglas contables.
-- Solo consultan datos. Cada consulta de reglas debe devolver 0 filas.
--
--   psql -h <host> -U contabilidad_admin -d contabilidad_db -f sql/05_verificacion.sql
-- =============================================================================

\echo '1. Tablas del esquema (esperado: 12)'
SELECT count(*) AS tablas
FROM information_schema.tables
WHERE table_schema = 'public' AND table_type = 'BASE TABLE';

\echo '2. Restricciones por tipo (esperado: c=15, f=17, p=12, u=12, x=1)'
SELECT contype::text AS tipo, count(*) AS cantidad
FROM pg_constraint
WHERE connamespace = 'public'::regnamespace
GROUP BY contype ORDER BY contype;

\echo '3. Partida doble: asientos con debe distinto del haber (esperado: 0 filas)'
SELECT id_asiento, SUM(debe) AS debe, SUM(haber) AS haber
FROM movimiento
GROUP BY id_asiento
HAVING SUM(debe) <> SUM(haber);

\echo '4. Movimientos en cuentas que no aceptan movimiento (esperado: 0 filas)'
SELECT m.id_movimiento, pc.codigo
FROM movimiento m JOIN plan_cuenta pc ON pc.id_cuenta = m.id_cuenta
WHERE NOT pc.acepta_movimiento;

\echo '5. Cuenta, tercero o centro de costo de otra empresa (esperado: 0 filas)'
SELECT m.id_movimiento
FROM movimiento m
JOIN asiento a           ON a.id_asiento = m.id_asiento
JOIN periodo_contable p  ON p.id_periodo = a.id_periodo
JOIN plan_cuenta pc      ON pc.id_cuenta = m.id_cuenta
LEFT JOIN tercero t      ON t.id_tercero = m.id_tercero
LEFT JOIN centro_costo c ON c.id_centro_costo = m.id_centro_costo
WHERE pc.id_empresa <> p.id_empresa
   OR t.id_empresa <> p.id_empresa
   OR c.id_empresa <> p.id_empresa;

\echo '6. Asientos con fecha fuera de su periodo (esperado: 0 filas)'
SELECT a.id_asiento, a.fecha, p.fecha_inicio, p.fecha_fin
FROM asiento a JOIN periodo_contable p ON p.id_periodo = a.id_periodo
WHERE a.fecha NOT BETWEEN p.fecha_inicio AND p.fecha_fin;

\echo '7. Ecuación contable por empresa con asientos contabilizados (diferencia esperada: 0)'
WITH saldos AS (
    SELECT p.id_empresa, tc.clase,
           SUM(m.debe - m.haber) AS saldo_deudor
    FROM movimiento m
    JOIN asiento a          ON a.id_asiento = m.id_asiento AND a.estado = 'CONTABILIZADO'
    JOIN periodo_contable p ON p.id_periodo = a.id_periodo
    JOIN plan_cuenta pc     ON pc.id_cuenta = m.id_cuenta
    JOIN tipo_cuenta tc     ON tc.id_tipo_cuenta = pc.id_tipo_cuenta
    GROUP BY p.id_empresa, tc.clase
)
SELECT id_empresa,
       SUM(saldo_deudor) FILTER (WHERE clase = 'ACTIVO')                                  AS activo,
       -SUM(saldo_deudor) FILTER (WHERE clase = 'PASIVO')                                 AS pasivo,
       -SUM(saldo_deudor) FILTER (WHERE clase IN ('PATRIMONIO','INGRESO','COSTO','GASTO')) AS patrimonio_mas_resultado,
       SUM(saldo_deudor)                                                                  AS diferencia
FROM saldos
GROUP BY id_empresa
ORDER BY id_empresa;
