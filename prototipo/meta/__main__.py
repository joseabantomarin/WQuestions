"""Entry point: `PYTHONPATH=prototipo python3 -m meta` — corre el menú en la terminal."""
import os

from . import seed, runtime

DB_PATH = os.path.join(os.path.dirname(__file__), "wq.db")


def main():
    conn, u = seed.abrir_universo(DB_PATH)
    try:
        runtime.run(u)
    except (EOFError, KeyboardInterrupt):
        print("\nHasta luego.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
