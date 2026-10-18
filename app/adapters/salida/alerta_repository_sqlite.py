"""ADAPTADOR de salida: implementa el puerto de persistencia con SQLite."""
import sqlite3
from datetime import datetime
from typing import List
from app.domain.alerta import Alerta
from app.ports.alerta_repository import AlertaRepositoryPort


class AlertaRepositorySQLite(AlertaRepositoryPort):
    def __init__(self, db_path: str):
        self.db_path = db_path

    def guardar(self, alerta: Alerta) -> Alerta:
        # INSERT parametrizado (evita SQL injection); el try/except cubre CA-03 (error de persistencia)
        try:
            with sqlite3.connect(self.db_path) as conn:
                cur = conn.execute(
                    """INSERT INTO Alertas (bus_id, velocidad_movimiento, acercamiento_brusco,
                       prediccion_agresion, fecha_hora, estado_envio, latitud, longitud)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (alerta.bus_id, alerta.velocidad_movimiento, alerta.acercamiento_brusco,
                     alerta.prediccion_agresion, alerta.fecha_hora.isoformat(timespec="seconds"),
                     alerta.estado_envio, alerta.latitud, alerta.longitud),
                )
                alerta.id = cur.lastrowid
                return alerta
        except sqlite3.Error as e:
            raise RuntimeError(f"Error al guardar la alerta: {e}") from e

    def actualizar_estado(self, alerta_id: int, nuevo_estado: str) -> None:
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("UPDATE Alertas SET estado_envio = ? WHERE id = ?",
                             (nuevo_estado, alerta_id))
        except sqlite3.Error as e:
            raise RuntimeError(f"Error al actualizar el estado: {e}") from e

    def listar(self) -> List[Alerta]:
        # SELECT de evidencia: devuelve todas las alertas persistidas
        try:
            with sqlite3.connect(self.db_path) as conn:
                filas = conn.execute(
                    """SELECT id, bus_id, velocidad_movimiento, acercamiento_brusco,
                       prediccion_agresion, fecha_hora, estado_envio, latitud, longitud
                       FROM Alertas ORDER BY id""").fetchall()
        except sqlite3.Error as e:
            raise RuntimeError(f"Error al consultar alertas: {e}") from e
        return [Alerta(id=f[0], bus_id=f[1], velocidad_movimiento=f[2], acercamiento_brusco=f[3],
                       prediccion_agresion=f[4], fecha_hora=datetime.fromisoformat(f[5]),
                       estado_envio=f[6], latitud=f[7], longitud=f[8]) for f in filas]
