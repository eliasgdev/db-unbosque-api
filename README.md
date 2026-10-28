# DB Unbosque API

API de solo lectura con FastAPI para el sistema contable (Balance General y Estado de Resultados).

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env
.venv/bin/uvicorn app.main:app --reload
```

Docs: http://localhost:8000/docs

## Endpoints

| Método | Ruta | Descripción |
| --- | --- | --- |
| GET | `/empresas` | Empresas |
| GET | `/empresas/{nit}` | Empresa |
| GET | `/empresas/{nit}/periodos` | Periodos contables |
| GET | `/empresas/{nit}/cuentas` | Plan de cuentas |
| GET | `/periodos/{id}/asientos` | Asientos del periodo |
| GET | `/asientos/{id}/movimientos` | Movimientos del asiento |
| GET | `/reportes/estado-resultados?periodo_id=` | Estado de Resultados |
| GET | `/reportes/balance-general?nit=&fecha_corte=` | Balance General |

Los reportes solo incluyen asientos con estado `CONTABILIZADO`.
