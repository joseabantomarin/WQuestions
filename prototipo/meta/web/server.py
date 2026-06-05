"""Servidor HTTP del menú meta-driven: API JSON + estáticos. Single-user, localhost."""
import json
import os
import sqlite3
from http.server import BaseHTTPRequestHandler, HTTPServer

from wq import SignatureError
from ..engine import MenuSession
from ..seed import abrir_universo
from .. import storage

_STATIC = os.path.abspath(os.path.join(os.path.dirname(__file__), "static"))
_MIME = {
    ".html": "text/html; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
    ".css": "text/css; charset=utf-8",
}


def crear_handler(estado):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):  # silencia el log por request
            pass

        def _enviar_json(self, obj, code=200):
            body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _payload(self):
            s = estado["sesion"]
            return {"estado": s.estado(), "tripletas": s.tripletas_visibles()}

        def _enviar_estatico(self, nombre):
            ruta = os.path.abspath(os.path.join(_STATIC, nombre))
            if not (ruta == _STATIC or ruta.startswith(_STATIC + os.sep)) or not os.path.isfile(ruta):
                self.send_error(404)
                return
            with open(ruta, "rb") as f:
                body = f.read()
            ext = os.path.splitext(ruta)[1]
            self.send_response(200)
            self.send_header("Content-Type", _MIME.get(ext, "application/octet-stream"))
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            if self.path in ("/", "/index.html"):
                self._enviar_estatico("index.html")
            elif self.path.startswith("/static/"):
                self._enviar_estatico(self.path[len("/static/"):])
            elif self.path == "/api/estado":
                self._enviar_json(self._payload())
            else:
                self.send_error(404)

        def do_POST(self):
            length = int(self.headers.get("Content-Length", 0) or 0)
            raw = self.rfile.read(length) if length else b""
            if self.path == "/api/seleccionar":
                try:
                    indice = int(json.loads(raw or b"{}")["indice"])
                except (KeyError, ValueError, TypeError, json.JSONDecodeError):
                    self._enviar_json({"error": "indice inválido"}, 400)
                    return
                efecto = estado["sesion"].seleccionar(indice)["efecto"]
                payload = self._payload()
                payload["efecto"] = efecto
                self._enviar_json(payload)
            elif self.path == "/api/reiniciar":
                estado["sesion"] = MenuSession(estado["universe"])
                self._enviar_json(self._payload())
            elif self.path == "/api/abrir_formulario":
                try:
                    datos = json.loads(raw or b"{}")
                    entidad = datos["entidad"]
                    registro_id = datos.get("registro_id")
                except (KeyError, ValueError, TypeError, json.JSONDecodeError):
                    self._enviar_json({"error": "datos inválidos"}, 400)
                    return
                from ..engine import efecto_formulario
                u = estado["universe"]
                try:
                    tipo = u.ind(entidad)
                    ef = efecto_formulario(u, tipo, "Editar " + (tipo.label or entidad),
                                           registro_id)
                except (SignatureError, ValueError, KeyError) as e:
                    self._enviar_json({"error": str(e)}, 400)
                    return
                self._enviar_json({"efecto": ef})
            elif self.path == "/api/guardar":
                try:
                    datos = json.loads(raw or b"{}")
                    entidad = datos["entidad"]
                    valores = datos["valores"]
                except (KeyError, ValueError, TypeError, json.JSONDecodeError):
                    self._enviar_json({"error": "datos inválidos"}, 400)
                    return
                from ..engine import guardar
                u = estado["universe"]
                try:
                    rid = guardar(u, entidad, valores, datos.get("registro_id"))
                except (SignatureError, ValueError, KeyError) as e:
                    self._enviar_json({"error": str(e)}, 400)
                    return
                conn = sqlite3.connect(estado["db_path"])
                storage.save(u, conn)
                conn.close()
                self._enviar_json({"ok": True, "registro_id": rid})
            else:
                self.send_error(404)

    return Handler


def crear_servidor(db_path, host="127.0.0.1", port=8000):
    """Carga el universo (siembra si hace falta) y devuelve (httpd, estado)."""
    conn, u = abrir_universo(db_path)
    conn.close()
    estado = {"universe": u, "sesion": MenuSession(u), "db_path": db_path}
    httpd = HTTPServer((host, port), crear_handler(estado))
    return httpd, estado
