# SISTEP Vision Guardian AI – PMV1 (backend)

Detección de forcejeo/asalto con Random Forest y registro de alertas en SQLite.
Arquitectura **hexagonal** (dominio, aplicación, puertos, adaptadores).

## Instalación
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python entrenar_modelo.py        # genera models/modelo_rf.pkl
```
## Ejecución
```bash
python main.py                   # demo con el evento [94, 1]
python -m tests.test_simulacion  # evidencia PDCA (3 casos + SELECT)
```
Para probar sin sklearn: `MODEL_BACKEND=mock` en `.env`.
