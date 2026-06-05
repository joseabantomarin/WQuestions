"""python -m meta.web → arranca el servidor del menú meta-driven."""
import os
import webbrowser

from .server import crear_servidor

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "menu.db")
HOST, PORT = "127.0.0.1", 8000


def main():
    httpd, _ = crear_servidor(DB_PATH, HOST, PORT)
    url = f"http://{HOST}:{PORT}/"
    print(f"Menú meta-driven en {url}  (Ctrl-C para detener)")
    try:
        webbrowser.open(url)
    except Exception:
        pass
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido.")
    finally:
        httpd.server_close()


if __name__ == "__main__":
    main()
