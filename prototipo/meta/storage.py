"""Persistencia SQLite de un Universe de wq (almacén; carga-en-memoria).

Dos tablas que espejan el modelo: `individuos` y `hechos`. El runtime solo usa
`load()`; promover a SQLite-consultado-directo después = reemplazar `load()`.
"""
import json
import sqlite3

from wq import Universe, Individual, Axis

_SCHEMA = """
CREATE TABLE IF NOT EXISTS individuos(
    id TEXT PRIMARY KEY,
    eje TEXT NOT NULL,
    label TEXT,
    payload TEXT
);
CREATE TABLE IF NOT EXISTS hechos(
    rowid INTEGER PRIMARY KEY AUTOINCREMENT,
    sujeto TEXT NOT NULL,
    rol TEXT NOT NULL,
    valor TEXT NOT NULL,
    valid_from TEXT,
    valid_to TEXT,
    tx_time TEXT
);
CREATE INDEX IF NOT EXISTS ix_hechos_sujeto ON hechos(sujeto);
CREATE INDEX IF NOT EXISTS ix_hechos_rol ON hechos(rol);
"""


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(_SCHEMA)
    conn.commit()


def save(universe: Universe, conn: sqlite3.Connection) -> None:
    init_db(conn)
    conn.execute("DELETE FROM hechos")
    conn.execute("DELETE FROM individuos")
    for ind in universe.individuals.values():
        conn.execute(
            "INSERT INTO individuos(id, eje, label, payload) VALUES (?, ?, ?, ?)",
            (ind.id, ind.axis.value, ind.label,
             json.dumps(ind.payload) if ind.payload is not None else None),
        )
    for f in universe.facts:
        conn.execute(
            "INSERT INTO hechos(sujeto, rol, valor, valid_from, valid_to, tx_time) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (f.subject.id, f.role, f.value.id,
             f.valid_from.isoformat() if f.valid_from else None,
             f.valid_to.isoformat() if f.valid_to else None,
             f.tx_time.isoformat() if f.tx_time else None),
        )
    conn.commit()


def load(conn: sqlite3.Connection, catalog) -> Universe:
    init_db(conn)
    u = Universe(catalog=catalog)
    inds = {}
    for id_, eje, label, payload in conn.execute(
            "SELECT id, eje, label, payload FROM individuos"):
        ind = Individual(
            id=id_, axis=Axis(eje), label=label,
            payload=json.loads(payload) if payload is not None else None,
        )
        inds[id_] = ind
        u.add_individual(ind)
    # v1: los hechos del menú son atemporales; load() ignora valid_from/valid_to/tx_time
    # (assert_fact regenera tx_time). Restaurar la vigencia es trabajo de una versión futura.
    for sujeto, rol, valor in conn.execute(
            "SELECT sujeto, rol, valor FROM hechos ORDER BY rowid"):
        u.assert_fact(inds[sujeto], rol, inds[valor])
    return u
