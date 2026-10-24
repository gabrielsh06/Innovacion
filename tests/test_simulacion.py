"""Evidencia PDCA (fase CHECK): ejecuta casos de prueba y consulta la BD.
Uso:  python -m tests.test_simulacion"""
import os
import sqlite3
from app.infrastructure import config
from app.infrastructure.container import construir_controlador
from app.application.procesar_evento import ProcesarEventoUseCase
from app.domain.alerta import EventoCamara
from app.adapters.salida.modelo_mock import ModeloMock
from app.ports.alerta_repository import AlertaRepositoryPort

DB_TEST = "sistep_test.db"


class RepositorioFallo(AlertaRepositoryPort):
    def guardar(self, alerta):
        raise RuntimeError("Error controlado de persistencia")

    def actualizar_estado(self, alerta_id, nuevo_estado):
        raise AssertionError("No debe actualizarse un estado sin alerta guardada")

    def listar(self):
        return []


def main():
    if os.path.exists(DB_TEST):
        os.remove(DB_TEST)  # BD limpia en cada corrida
    controlador, repo = construir_controlador(db_path=DB_TEST)
    resultados = []

    def caso(id_, descripcion, bus, vel, acer, lat, lon, esperado):
        print(f"\n--- {id_}: {descripcion} (vel={vel}, acercamiento={acer}) ---")
        r = controlador.recibir_evento(bus, vel, acer, lat, lon)
        ok = (r.prediccion == esperado) and ((r.alerta is not None) == bool(esperado))
        print(f"   Predicción={r.prediccion} | Alerta guardada={'SÍ' if r.alerta else 'NO'} "
              f"| Resultado: {'APROBADA' if ok else 'FALLIDA'}")
        resultados.append((id_, ok))

    # CP-01 / CA-01: amenaza válida, se registra y queda enviada.
    caso("CP-01", "Registro exitoso de amenaza", "BUS-302", 95, 1,
         -12.0911, -77.0230, 1)

    # CP-02 / CA-02: entrada inválida, se rechaza antes de persistir.
    print("\n--- CP-02: velocidad fuera de rango (150) ---")
    try:
        controlador.recibir_evento("BUS-302", 150, 1)
        resultados.append(("CP-02", False))
        print("   Resultado: FALLIDA (aceptó dato inválido)")
    except ValueError as e:
        resultados.append(("CP-02", True))
        print(f"   Rechazado: {e} | Resultado: APROBADA")

    # CP-03 / CA-03: si falla la persistencia no se devuelve confirmación falsa.
    print("\n--- CP-03: error controlado de persistencia ---")
    caso_uso = ProcesarEventoUseCase(ModeloMock(), RepositorioFallo())
    try:
        caso_uso.ejecutar(EventoCamara("BUS-302", 95, 1))
        resultados.append(("CP-03", False))
        print("   Resultado: FALLIDA (confirmó una alerta no guardada)")
    except RuntimeError as e:
        resultados.append(("CP-03", True))
        print(f"   Error controlado: {e} | Resultado: APROBADA")

    # SELECT de evidencia directo a la BD
    print("\n=== SELECT * FROM Alertas ===")
    with sqlite3.connect(DB_TEST) as conn:
        filas = conn.execute("SELECT id, bus_id, velocidad_movimiento, acercamiento_brusco, "
                             "prediccion_agresion, fecha_hora, estado_envio, latitud, longitud "
                             "FROM Alertas").fetchall()
    for f in filas:
        print("  ", f)
    ok_bd = len(filas) == 1 and filas[0][4] == 1 and filas[0][6] == "ENVIADO_PNP"
    resultados.append(("BD", ok_bd))
    print(f"\nFilas persistidas: {len(filas)} (esperado: 1) -> {'APROBADA' if ok_bd else 'FALLIDA'}")

    print("\n=== RESUMEN ===")
    for id_, ok in resultados:
        print(f"  {id_}: {'APROBADA' if ok else 'FALLIDA'}")
    raise SystemExit(0 if all(ok for _, ok in resultados) else 1)


if __name__ == "__main__":
    main()
