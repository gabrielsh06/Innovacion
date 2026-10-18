"""INFRAESTRUCTURA: creación del esquema SQLite (tabla Alertas)."""
import sqlite3

DDL_ALERTAS = """
CREATE TABLE IF NOT EXISTS Alertas (
    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
    bus_id                TEXT    NOT NULL,
    velocidad_movimiento  INTEGER NOT NULL CHECK (velocidad_movimiento BETWEEN 0 AND 100),
    acercamiento_brusco   INTEGER NOT NULL CHECK (acercamiento_brusco IN (0, 1)),
    prediccion_agresion   INTEGER NOT NULL CHECK (prediccion_agresion IN (0, 1)),
    fecha_hora            TEXT    NOT NULL,
    estado_envio          TEXT    NOT NULL,
    latitud               REAL,
    longitud              REAL
);
"""


def inicializar_bd(db_path: str) -> None:
    """Crea la BD y la tabla si no existen."""
    try:
        with sqlite3.connect(db_path) as conn:
            conn.execute(DDL_ALERTAS)
    except sqlite3.Error as e:
        raise RuntimeError(f"No se pudo inicializar la base de datos: {e}") from e
