"""Evidencia PDCA (fase CHECK): ejecuta casos de prueba y consulta la BD.
Uso:  python -m tests.test_simulacion"""
import os
import sqlite3
from app.infrastructure import config
from app.infrastructure.container import construir_controlador

DB_TEST = "sistep_test.db"


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

    # CP-01: caso normal, NO debe guardar alerta
    caso("CP-01", "Contacto normal / aglomeración", "BUS-302", 15, 0, -12.0464, -77.0428, 0)
    # CP-02: caso asalto, SÍ debe guardar alerta
    caso("CP-02", "Forcejeo / asalto", "BUS-302", 95, 1, -12.0911, -77.0230, 1)

    # CP-03: entrada inválida debe rechazarse (validación de dominio)
    print("\n--- CP-03: velocidad fuera de rango (150) ---")
    try:
        controlador.recibir_evento("BUS-302", 150, 1)
        resultados.append(("CP-03", False))
        print("   Resultado: FALLIDA (aceptó dato inválido)")
    except ValueError as e:
        resultados.append(("CP-03", True))
        print(f"   Rechazado: {e} | Resultado: APROBADA")

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
