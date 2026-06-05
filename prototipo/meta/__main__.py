"""Entry point: `PYTHONPATH=prototipo python3 -m meta`.

Abre (o crea) la BD SQLite del menú; si está vacía, la siembra; carga el universo
y corre el evaluador.
"""
import os
import sqlite3

from .catalogo_app import build_catalog
from . import storage, seed, runtime

DB_PATH = os.path.join(os.path.dirname(__file__), "menu.db")


def main():
    conn = sqlite3.connect(DB_PATH)
    storage.init_db(conn)
    vacio = conn.execute("SELECT COUNT(*) FROM hechos").fetchone()[0] == 0
    if vacio:
        seed.seed(conn)
    u = storage.load(conn, build_catalog())
    try:
        runtime.run(u)
    except (EOFError, KeyboardInterrupt):
        print("\nHasta luego.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
