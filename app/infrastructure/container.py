"""INFRAESTRUCTURA: ensambla adaptadores y caso de uso (inyección de dependencias)."""
from app.adapters.entrada.evento_controller import EventoController
from app.adapters.salida.alerta_repository_sqlite import AlertaRepositorySQLite
from app.adapters.salida.modelo_mock import ModeloMock
from app.application.procesar_evento import ProcesarEventoUseCase
from app.infrastructure import config
from app.infrastructure.database import inicializar_bd


def construir_controlador(db_path=None, backend=None, model_path=None):
    db_path = db_path or config.DB_PATH
    backend = backend or config.MODEL_BACKEND
    model_path = model_path or config.MODEL_PATH
    inicializar_bd(db_path)
    if backend == "mock":
        modelo = ModeloMock()
    else:
        from app.adapters.salida.modelo_random_forest import ModeloRandomForest
        modelo = ModeloRandomForest(model_path)
    repo = AlertaRepositorySQLite(db_path)
    return EventoController(ProcesarEventoUseCase(modelo, repo)), repo
