import json
import os
import tempfile
import threading
import unittest
import urllib.error
import urllib.request

from meta.web.server import crear_servidor


class TestWebAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = os.path.join(tempfile.mkdtemp(), "menu.db")
        cls.httpd, cls.estado = crear_servidor(cls.db, "127.0.0.1", 0)
        cls.port = cls.httpd.server_address[1]
        cls.hilo = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.hilo.start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()

    def _url(self, ruta):
        return f"http://127.0.0.1:{self.port}{ruta}"

    def _get(self, ruta):
        with urllib.request.urlopen(self._url(ruta)) as r:
            return json.loads(r.read())

    def _post(self, ruta, obj=None):
        data = json.dumps(obj).encode() if obj is not None else b""
        req = urllib.request.Request(self._url(ruta), data=data,
                                     headers={"Content-Type": "application/json"},
                                     method="POST")
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read())

    def setUp(self):
        self._post("/api/reiniciar")  # estado limpio por test

    def test_estado_inicial(self):
        d = self._get("/api/estado")
        self.assertEqual(d["estado"]["titulo"], "Menú principal")
        self.assertEqual(len(d["estado"]["opciones"]), 4)
        self.assertTrue(any(t["rol"] == "tiene_opcion" for t in d["tripletas"]))

    def test_seleccionar_navega_submenu(self):
        d = self._post("/api/seleccionar", {"indice": 2})
        self.assertEqual(d["efecto"]["tipo"], "navegado")
        self.assertEqual(d["estado"]["titulo"], "Configuración")

    def test_reiniciar_vuelve_al_principal(self):
        self._post("/api/seleccionar", {"indice": 2})
        d = self._post("/api/reiniciar")
        self.assertEqual(d["estado"]["titulo"], "Menú principal")
        self.assertFalse(d["estado"]["es_submenu"])

    def test_index_html_se_sirve(self):
        with urllib.request.urlopen(self._url("/")) as r:
            self.assertEqual(r.status, 200)
            self.assertIn(b"meta-driven", r.read())

    def test_traversal_estatico_bloqueado(self):
        with self.assertRaises(urllib.error.HTTPError) as cm:
            urllib.request.urlopen(self._url("/static/../server.py"))
        self.assertEqual(cm.exception.code, 404)

    def test_body_malformado_da_400(self):
        req = urllib.request.Request(
            self._url("/api/seleccionar"), data=b"no-es-json",
            headers={"Content-Type": "application/json"}, method="POST")
        with self.assertRaises(urllib.error.HTTPError) as cm:
            urllib.request.urlopen(req)
        self.assertEqual(cm.exception.code, 400)


if __name__ == "__main__":
    unittest.main()
