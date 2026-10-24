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

## Pruebas y mejora mediante PDCA

La evidencia ejecutable del PMV1 se encuentra en
`tests/test_simulacion.py` y se ejecuta con:

```bash
python -m tests.test_simulacion
```

La prueba registra el resultado real como `APROBADA` o `FALLIDA`:

| Prueba | Criterio verificado | Resultado esperado |
|---|---|---|
| CP-01 | CA-01: amenaza válida | La alerta se persiste y queda `ENVIADO_PNP` |
| CP-02 | CA-02: entrada inválida | Se rechaza una velocidad fuera de rango |
| CP-03 | CA-03: error controlado | No se confirma una alerta que no pudo persistirse |

La mejora aplicada consiste en validar los datos en `EventoCamara` antes de
consultar el modelo o guardar la alerta. También se prueba explícitamente el
fallo de persistencia para evitar una confirmación falsa. La salida de consola
de la ejecución constituye la evidencia del ciclo PDCA: planificar los casos,
ejecutarlos, verificar su resultado y conservarlos como pruebas recurrentes.
