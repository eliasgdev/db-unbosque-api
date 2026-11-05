-- =============================================================================
-- 04_algebra_relacional.sql
-- Scripts varios: las 51 sentencias de álgebra relacional del proyecto,
-- traducidas a SQL de PostgreSQL. Solo consultan datos (no modifican nada).
--
-- Ejecución (después de 01 y 02):
--   psql -h <host> -U contabilidad_admin -d contabilidad_db -f sql/04_algebra_relacional.sql
--
-- Abreviaturas del álgebra: PC = plan_cuenta, TC = tipo_cuenta, RE = rubro_estado,
-- PER = periodo_contable, AS = asiento, MOV = movimiento.
-- La división (÷) se expresa con NOT EXISTS ( ... EXCEPT ... ).
-- "Filas esperadas" corresponde a los datos de 02_seed_datos_realistas.sql.
-- =============================================================================

-- 01. Nombre de todas las cuentas de la empresa 1
--     Álgebra: π nombre (σ id_empresa=1 (PC))
--     Filas esperadas: 89
\echo 01. Nombre de todas las cuentas de la empresa 1
SELECT DISTINCT nombre FROM plan_cuenta WHERE id_empresa = 1;

-- 02. Código y nombre de las cuentas que aceptan movimiento
--     Álgebra: π codigo, nombre (σ acepta_movimiento=TRUE (PC))
--     Filas esperadas: 52
\echo 02. Código y nombre de las cuentas que aceptan movimiento
SELECT DISTINCT codigo, nombre FROM plan_cuenta WHERE acepta_movimiento = TRUE;

-- 03. Cuentas de nivel 1
--     Álgebra: σ nivel=1 (PC)
--     Filas esperadas: 20
\echo 03. Cuentas de nivel 1
SELECT * FROM plan_cuenta WHERE nivel = 1;

-- 04. Tipos de cuenta de naturaleza deudora
--     Álgebra: π id_tipo_cuenta (σ naturaleza='DEBITO' (TC))
--     Filas esperadas: 3
\echo 04. Tipos de cuenta de naturaleza deudora
SELECT DISTINCT id_tipo_cuenta FROM tipo_cuenta WHERE naturaleza = 'DEBITO';

-- 05. Periodos abiertos de la empresa 1
--     Álgebra: σ id_empresa=1 ∧ estado='ABIERTO' (PER)
--     Filas esperadas: 1
\echo 05. Periodos abiertos de la empresa 1
SELECT * FROM periodo_contable WHERE id_empresa = 1 AND estado = 'ABIERTO';

-- 06. Cuentas raíz (sin cuenta padre)
--     Álgebra: σ id_cuenta_padre IS NULL (PC)
--     Filas esperadas: 20
\echo 06. Cuentas raíz (sin cuenta padre)
SELECT * FROM plan_cuenta WHERE id_cuenta_padre IS NULL;

-- 07. Cuentas de la empresa 2 con nivel mayor que 2
--     Álgebra: σ id_empresa=2 ∧ nivel>2 (PC)
--     Filas esperadas: 0
\echo 07. Cuentas de la empresa 2 con nivel mayor que 2
SELECT * FROM plan_cuenta WHERE id_empresa = 2 AND nivel > 2;

-- 08. Cuentas cuyo código empieza por 1
--     Álgebra: σ codigo LIKE '1%' (PC)
--     Filas esperadas: 33
\echo 08. Cuentas cuyo código empieza por 1
SELECT * FROM plan_cuenta WHERE codigo LIKE '1%';

-- 09. Movimientos débito (debe mayor que cero)
--     Álgebra: σ debe>0 (MOV)
--     Filas esperadas: 77
\echo 09. Movimientos débito (debe mayor que cero)
SELECT * FROM movimiento WHERE debe > 0;

-- 10. Movimientos con haber 0 y debe mayor que 1.000
--     Álgebra: σ haber=0 ∧ debe>1000 (MOV)
--     Filas esperadas: 77
\echo 10. Movimientos con haber 0 y debe mayor que 1.000
SELECT * FROM movimiento WHERE haber = 0 AND debe > 1000;

-- 11. Asientos del periodo 3 de la empresa 1
--     Álgebra: π id_asiento, numero, fecha (σ AS.id_periodo=3 ∧ id_empresa=1 (AS ⋈ AS.id_periodo=PER.id_periodo PER))
--     Filas esperadas: 12
\echo 11. Asientos del periodo 3 de la empresa 1
SELECT DISTINCT a.id_asiento, a.numero, a.fecha FROM asiento a JOIN periodo_contable p ON a.id_periodo = p.id_periodo WHERE a.id_periodo = 3 AND p.id_empresa = 1;

-- 12. Periodos que inician en 2026
--     Álgebra: σ fecha_inicio ≥ '2026-01-01' ∧ fecha_inicio ≤ '2026-12-31' (PER)
--     Filas esperadas: 5
\echo 12. Periodos que inician en 2026
SELECT * FROM periodo_contable WHERE fecha_inicio BETWEEN DATE '2026-01-01' AND DATE '2026-12-31';

-- 13. Tipos de cuenta de clase ACTIVO
--     Álgebra: σ clase='ACTIVO' (TC)
--     Filas esperadas: 2
\echo 13. Tipos de cuenta de clase ACTIVO
SELECT * FROM tipo_cuenta WHERE clase = 'ACTIVO';

-- 14. Renombrar PC como CUENTA y listar sus nombres
--     Álgebra: π nombre (ρ CUENTA (PC))
--     Filas esperadas: 107
\echo 14. Renombrar PC como CUENTA y listar sus nombres
SELECT DISTINCT cuenta.nombre FROM plan_cuenta AS cuenta;

-- 15. Movimientos cuyo asiento pertenece al periodo 5
--     Álgebra: π id_movimiento (MOV ⋈ σ id_periodo=5 (AS))
--     Filas esperadas: 7
\echo 15. Movimientos cuyo asiento pertenece al periodo 5
SELECT DISTINCT m.id_movimiento FROM movimiento m JOIN asiento a ON m.id_asiento = a.id_asiento WHERE a.id_periodo = 5;

-- 16. Cuentas con su tipo
--     Álgebra: PC ⋈ TC
--     Filas esperadas: 113
\echo 16. Cuentas con su tipo
SELECT * FROM plan_cuenta pc JOIN tipo_cuenta tc USING (id_tipo_cuenta);

-- 17. Cuentas con su rubro
--     Álgebra: PC ⋈ PC.id_rubro=RE.id_rubro RE
--     Filas esperadas: 113
\echo 17. Cuentas con su rubro
SELECT * FROM plan_cuenta pc JOIN rubro_estado re ON pc.id_rubro = re.id_rubro;

-- 18. Cuentas de la empresa 1 con clase y naturaleza
--     Álgebra: π codigo, nombre, clase, naturaleza (σ id_empresa=1 (PC ⋈ TC))
--     Filas esperadas: 90
\echo 18. Cuentas de la empresa 1 con clase y naturaleza
SELECT DISTINCT pc.codigo, pc.nombre, tc.clase, tc.naturaleza FROM plan_cuenta pc JOIN tipo_cuenta tc USING (id_tipo_cuenta) WHERE pc.id_empresa = 1;

-- 19. Cuentas sin movimientos
--     Álgebra: π id_cuenta (PC) − π id_cuenta (MOV)
--     Filas esperadas: 63
\echo 19. Cuentas sin movimientos
SELECT id_cuenta FROM plan_cuenta EXCEPT SELECT id_cuenta FROM movimiento;

-- 20. Cuentas con al menos un movimiento
--     Álgebra: π id_cuenta (MOV)
--     Filas esperadas: 50
\echo 20. Cuentas con al menos un movimiento
SELECT DISTINCT id_cuenta FROM movimiento;

-- 21. Asientos con su periodo y empresa
--     Álgebra: AS ⋈ AS.id_periodo=PER.id_periodo PER
--     Filas esperadas: 31
\echo 21. Asientos con su periodo y empresa
SELECT * FROM asiento a JOIN periodo_contable p ON a.id_periodo = p.id_periodo;

-- 22. Movimientos con datos de cuenta y asiento
--     Álgebra: MOV ⋈ PC ⋈ AS
--     Filas esperadas: 152
\echo 22. Movimientos con datos de cuenta y asiento
SELECT * FROM movimiento m JOIN plan_cuenta pc ON m.id_cuenta = pc.id_cuenta JOIN asiento a ON m.id_asiento = a.id_asiento;

-- 23. Periodos cerrados o que inician en 2025
--     Álgebra: σ estado='CERRADO' (PER) ∪ σ fecha_inicio ≥ '2025-01-01' ∧ fecha_inicio ≤ '2025-12-31' (PER)
--     Filas esperadas: 6
\echo 23. Periodos cerrados o que inician en 2025
SELECT * FROM periodo_contable WHERE estado = 'CERRADO' UNION SELECT * FROM periodo_contable WHERE fecha_inicio BETWEEN DATE '2025-01-01' AND DATE '2025-12-31';

-- 24. Cuentas de clase ACTIVO o PASIVO
--     Álgebra: π id_cuenta (PC ⋈ σ clase='ACTIVO' (TC)) ∪ π id_cuenta (PC ⋈ σ clase='PASIVO' (TC))
--     Filas esperadas: 49
\echo 24. Cuentas de clase ACTIVO o PASIVO
SELECT pc.id_cuenta FROM plan_cuenta pc JOIN tipo_cuenta tc USING (id_tipo_cuenta) WHERE tc.clase = 'ACTIVO' UNION SELECT pc.id_cuenta FROM plan_cuenta pc JOIN tipo_cuenta tc USING (id_tipo_cuenta) WHERE tc.clase = 'PASIVO';

-- 25. Cuentas de clase ACTIVO que aceptan movimiento
--     Álgebra: π id_cuenta (PC ⋈ σ clase='ACTIVO' (TC)) ∩ π id_cuenta (σ acepta_movimiento=TRUE (PC))
--     Filas esperadas: 17
\echo 25. Cuentas de clase ACTIVO que aceptan movimiento
SELECT pc.id_cuenta FROM plan_cuenta pc JOIN tipo_cuenta tc USING (id_tipo_cuenta) WHERE tc.clase = 'ACTIVO' INTERSECT SELECT id_cuenta FROM plan_cuenta WHERE acepta_movimiento = TRUE;

-- 26. Hijas de la cuenta 10
--     Álgebra: σ id_cuenta_padre=10 (PC)
--     Filas esperadas: 1
\echo 26. Hijas de la cuenta 10
SELECT * FROM plan_cuenta WHERE id_cuenta_padre = 10;

-- 27. Cuentas que son padre de otra
--     Álgebra: π id_cuenta (PC) ∩ ρ X(id_cuenta) (π id_cuenta_padre (PC))
--     Filas esperadas: 61
\echo 27. Cuentas que son padre de otra
SELECT id_cuenta FROM plan_cuenta INTERSECT SELECT id_cuenta_padre AS id_cuenta FROM plan_cuenta;

-- 28. Cuentas sin hijas
--     Álgebra: π id_cuenta (PC) − ρ X(id_cuenta) (π id_cuenta_padre (σ id_cuenta_padre IS NOT NULL (PC)))
--     Filas esperadas: 52
\echo 28. Cuentas sin hijas
SELECT id_cuenta FROM plan_cuenta EXCEPT SELECT id_cuenta_padre AS id_cuenta FROM plan_cuenta WHERE id_cuenta_padre IS NOT NULL;

-- 29. Movimientos de cuentas de clase INGRESO
--     Álgebra: MOV ⋈ PC ⋈ σ clase='INGRESO' (TC)
--     Filas esperadas: 21
\echo 29. Movimientos de cuentas de clase INGRESO
SELECT m.* FROM movimiento m JOIN plan_cuenta pc ON m.id_cuenta = pc.id_cuenta JOIN tipo_cuenta tc ON pc.id_tipo_cuenta = tc.id_tipo_cuenta WHERE tc.clase = 'INGRESO';

-- 30. Cuentas de la empresa 1 que aceptan movimiento
--     Álgebra: π id_cuenta (σ id_empresa=1 (PC)) ∩ π id_cuenta (σ acepta_movimiento=TRUE (PC))
--     Filas esperadas: 35
\echo 30. Cuentas de la empresa 1 que aceptan movimiento
SELECT id_cuenta FROM plan_cuenta WHERE id_empresa = 1 INTERSECT SELECT id_cuenta FROM plan_cuenta WHERE acepta_movimiento = TRUE;

-- 31. Periodos sin asientos
--     Álgebra: π id_periodo (PER) − π id_periodo (AS)
--     Filas esperadas: 3
\echo 31. Periodos sin asientos
SELECT id_periodo FROM periodo_contable EXCEPT SELECT id_periodo FROM asiento;

-- 32. Cuentas acreedoras que aceptan movimiento, de la empresa 1
--     Álgebra: π codigo, nombre (σ id_empresa=1 ∧ acepta_movimiento=TRUE (PC ⋈ σ naturaleza='CREDITO' (TC)))
--     Filas esperadas: 12
\echo 32. Cuentas acreedoras que aceptan movimiento, de la empresa 1
SELECT DISTINCT pc.codigo, pc.nombre FROM plan_cuenta pc JOIN tipo_cuenta tc USING (id_tipo_cuenta) WHERE tc.naturaleza = 'CREDITO' AND pc.id_empresa = 1 AND pc.acepta_movimiento = TRUE;

-- 33. Movimientos de cuentas de nivel 1
--     Álgebra: MOV ⋈ σ nivel=1 (PC)
--     Filas esperadas: 9
\echo 33. Movimientos de cuentas de nivel 1
SELECT m.* FROM movimiento m JOIN plan_cuenta pc ON m.id_cuenta = pc.id_cuenta WHERE pc.nivel = 1;

-- 34. Cuentas de la empresa 1 del rubro de efectivo
--     Álgebra: π PC.id_cuenta, PC.codigo, PC.nombre (σ PC.id_empresa=1 (PC ⋈ PC.id_rubro=RE.id_rubro σ RE.nombre='Efectivo y Equivalentes de Efectivo' (RE)))
--     Filas esperadas: 10
\echo 34. Cuentas de la empresa 1 del rubro de efectivo
SELECT DISTINCT pc.id_cuenta, pc.codigo, pc.nombre FROM plan_cuenta pc JOIN rubro_estado re ON pc.id_rubro = re.id_rubro WHERE re.nombre = 'Efectivo y Equivalentes de Efectivo' AND pc.id_empresa = 1;

-- 35. Asientos con al menos un movimiento de una cuenta de clase PASIVO
--     Álgebra: π id_asiento (MOV ⋈ PC ⋈ σ clase='PASIVO' (TC))
--     Filas esperadas: 8
\echo 35. Asientos con al menos un movimiento de una cuenta de clase PASIVO
SELECT DISTINCT m.id_asiento FROM movimiento m JOIN plan_cuenta pc ON m.id_cuenta = pc.id_cuenta JOIN tipo_cuenta tc ON pc.id_tipo_cuenta = tc.id_tipo_cuenta WHERE tc.clase = 'PASIVO';

-- 36. Total del debe por cuenta
--     Álgebra: γ id_cuenta; SUM(debe) → total_debe (MOV)
--     Filas esperadas: 50
\echo 36. Total del debe por cuenta
SELECT id_cuenta, SUM(debe) AS total_debe FROM movimiento GROUP BY id_cuenta;

-- 37. Saldo por cuenta (debe menos haber)
--     Álgebra: γ id_cuenta; SUM(debe) − SUM(haber) → saldo (MOV)
--     Filas esperadas: 50
\echo 37. Saldo por cuenta (debe menos haber)
SELECT id_cuenta, SUM(debe) - SUM(haber) AS saldo FROM movimiento GROUP BY id_cuenta;

-- 38. Número de movimientos por asiento
--     Álgebra: γ id_asiento; COUNT(id_movimiento) → n (MOV)
--     Filas esperadas: 31
\echo 38. Número de movimientos por asiento
SELECT id_asiento, COUNT(id_movimiento) AS n FROM movimiento GROUP BY id_asiento;

-- 39. Cuentas con más de 10 movimientos
--     Álgebra: σ n>10 (γ id_cuenta; COUNT(id_movimiento) → n (MOV))
--     Filas esperadas: 1
\echo 39. Cuentas con más de 10 movimientos
SELECT id_cuenta, COUNT(id_movimiento) AS n FROM movimiento GROUP BY id_cuenta HAVING COUNT(id_movimiento) > 10;

-- 40. Saldo por clase de cuenta
--     Álgebra: γ clase; SUM(debe) − SUM(haber) → saldo (MOV ⋈ PC ⋈ TC)
--     Filas esperadas: 6
\echo 40. Saldo por clase de cuenta
SELECT tc.clase, SUM(m.debe) - SUM(m.haber) AS saldo FROM movimiento m JOIN plan_cuenta pc ON m.id_cuenta = pc.id_cuenta JOIN tipo_cuenta tc ON pc.id_tipo_cuenta = tc.id_tipo_cuenta GROUP BY tc.clase;

-- 41. Asientos cuyo debe total no coincide con el haber total
--     Álgebra: σ debe_total ≠ haber_total (γ id_asiento; SUM(debe) → debe_total, SUM(haber) → haber_total (MOV))
--     Filas esperadas: 0
\echo 41. Asientos cuyo debe total no coincide con el haber total
SELECT id_asiento, SUM(debe) AS debe_total, SUM(haber) AS haber_total FROM movimiento GROUP BY id_asiento HAVING SUM(debe) <> SUM(haber);

-- 42. Periodos con movimientos en todas las cuentas de clase ACTIVO
--     Álgebra: π id_periodo, id_cuenta (MOV ⋈ AS) ÷ π id_cuenta (PC ⋈ σ clase='ACTIVO' (TC))
--     Filas esperadas: 0
\echo 42. Periodos con movimientos en todas las cuentas de clase ACTIVO
SELECT p.id_periodo FROM periodo_contable p WHERE NOT EXISTS (SELECT pc.id_cuenta FROM plan_cuenta pc JOIN tipo_cuenta tc USING (id_tipo_cuenta) WHERE tc.clase = 'ACTIVO' EXCEPT SELECT m.id_cuenta FROM movimiento m JOIN asiento a ON m.id_asiento = a.id_asiento WHERE a.id_periodo = p.id_periodo);

-- 43. Empresas con cuentas de todos los tipos de cuenta
--     Álgebra: π id_empresa, id_tipo_cuenta (PC) ÷ π id_tipo_cuenta (TC)
--     Filas esperadas: 1
\echo 43. Empresas con cuentas de todos los tipos de cuenta
SELECT e.id_empresa FROM empresa e WHERE NOT EXISTS (SELECT id_tipo_cuenta FROM tipo_cuenta EXCEPT SELECT id_tipo_cuenta FROM plan_cuenta pc WHERE pc.id_empresa = e.id_empresa);

-- 44. Tipos de cuenta con al menos una cuenta en la empresa 1
--     Álgebra: π id_tipo_cuenta (σ id_empresa=1 (PC))
--     Filas esperadas: 7
\echo 44. Tipos de cuenta con al menos una cuenta en la empresa 1
SELECT DISTINCT id_tipo_cuenta FROM plan_cuenta WHERE id_empresa = 1;

-- 45. Código y nombre de las cuentas de activo de la empresa 1
--     Álgebra: π codigo, nombre (σ id_empresa=1 ∧ clase='ACTIVO' (PC ⋈ TC))
--     Filas esperadas: 27
\echo 45. Código y nombre de las cuentas de activo de la empresa 1
SELECT DISTINCT pc.codigo, pc.nombre FROM plan_cuenta pc JOIN tipo_cuenta tc USING (id_tipo_cuenta) WHERE pc.id_empresa = 1 AND tc.clase = 'ACTIVO';

-- 46. Periodos que inician en 2026 y siguen abiertos
--     Álgebra: π id_periodo (σ fecha_inicio ≥ '2026-01-01' ∧ fecha_inicio ≤ '2026-12-31' ∧ estado='ABIERTO' (PER))
--     Filas esperadas: 4
\echo 46. Periodos que inician en 2026 y siguen abiertos
SELECT id_periodo FROM periodo_contable WHERE fecha_inicio BETWEEN DATE '2026-01-01' AND DATE '2026-12-31' AND estado = 'ABIERTO';

-- 47. Movimientos de la cuenta 10
--     Álgebra: σ id_cuenta=10 (MOV)
--     Filas esperadas: 0
\echo 47. Movimientos de la cuenta 10
SELECT * FROM movimiento WHERE id_cuenta = 10;

-- 48. Tipos de cuenta acreedores o de clase PASIVO
--     Álgebra: π id_tipo_cuenta (σ naturaleza='CREDITO' (TC)) ∪ π id_tipo_cuenta (σ clase='PASIVO' (TC))
--     Filas esperadas: 4
\echo 48. Tipos de cuenta acreedores o de clase PASIVO
SELECT id_tipo_cuenta FROM tipo_cuenta WHERE naturaleza = 'CREDITO' UNION SELECT id_tipo_cuenta FROM tipo_cuenta WHERE clase = 'PASIVO';

-- 49. Tipos de cuenta sin ninguna cuenta en la empresa 1
--     Álgebra: π id_tipo_cuenta (TC) − π id_tipo_cuenta (σ id_empresa=1 (PC))
--     Filas esperadas: 0
\echo 49. Tipos de cuenta sin ninguna cuenta en la empresa 1
SELECT id_tipo_cuenta FROM tipo_cuenta EXCEPT SELECT id_tipo_cuenta FROM plan_cuenta WHERE id_empresa = 1;

-- 50. Movimientos con la fecha de su asiento
--     Álgebra: π id_movimiento, fecha (MOV ⋈ AS)
--     Filas esperadas: 152
\echo 50. Movimientos con la fecha de su asiento
SELECT DISTINCT m.id_movimiento, a.fecha FROM movimiento m JOIN asiento a ON m.id_asiento = a.id_asiento;

-- 51. Cantidad de movimientos de la cuenta 10
--     Álgebra: γ COUNT(id_movimiento) → total (σ id_cuenta=10 (MOV))
--     Filas esperadas: 1
\echo 51. Cantidad de movimientos de la cuenta 10
SELECT COUNT(id_movimiento) AS total FROM movimiento WHERE id_cuenta = 10;
