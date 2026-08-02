"""Banco de pruebas: ¿cuánto cuesta un evaluador de restricciones?

Mide sobre el prototipo real, no sobre una estimación. Tres preguntas:

1. ¿Cuánto cuesta hoy escribir un hecho? (línea base)
2. ¿Cuánto cuesta comprobar las restricciones AL ESCRIBIR?
3. ¿Cuánto cuesta comprobarlas A DEMANDA, en un barrido?

La respuesta decide el diseño, no al revés.
"""
import sys, time, statistics
sys.path.insert(0, "/Users/joseabanto/WQuestions/prototipo")

from wq import Axis, Individual, Universe, Catalog

ESCALAS = [1_000, 10_000, 100_000]


def cronometrar(fn, repeticiones=3):
    tiempos = []
    for _ in range(repeticiones):
        t0 = time.perf_counter()
        fn()
        tiempos.append(time.perf_counter() - t0)
    return min(tiempos)


def _valor(rol, i):
    """Un valor del eje que la signatura del rol exige."""
    if rol in ("disponibilidad", "monto"):
        return Individual(id=f"n_{i}", axis=Axis.N,
                          payload={"value": (i % 130), "unit": "K:Porcentaje"})
    if rol == "lugar_de":
        return Individual(id=f"l_{i % 50}", axis=Axis.L)
    if rol == "momento":
        return Individual(id=f"t_{i % 50}", axis=Axis.T)
    return Individual(id=f"k_{i % 50}", axis=Axis.K)


def universo(n_hechos, con_catalogo=True):
    u = Universe(catalog=Catalog() if con_catalogo else None)
    roles = ["disponibilidad", "monto", "estado", "lugar_de", "momento"]
    for i in range(n_hechos):
        s = Individual(id=f"sit_{i}", axis=Axis.O)
        rol = roles[i % len(roles)]
        v = _valor(rol, i)
        u.assert_fact(s, rol, v)
    return u


# ---------------------------------------------------------------------------
# La forma de una restricción: un rol objetivo y un predicado sobre el valor
# ---------------------------------------------------------------------------

class Forma:
    def __init__(self, rol, minimo=None, maximo=None):
        self.rol, self.minimo, self.maximo = rol, minimo, maximo

    def viola(self, hecho):
        p = hecho.value.payload
        if not isinstance(p, dict) or "value" not in p:
            return False
        v = p["value"]
        return ((self.minimo is not None and v < self.minimo)
                or (self.maximo is not None and v > self.maximo))


FORMAS = [Forma("disponibilidad", 0, 100), Forma("monto", 0, None)]
# Un catálogo realista tiene decenas de formas, no dos.
FORMAS_MUCHAS = FORMAS + [Forma(f"rol_inexistente_{i}", 0, 1) for i in range(48)]


def barrido_indexado(u, formas):
    """A demanda, usando el índice por rol: solo toca lo que la forma alcanza."""
    violaciones = 0
    for f in formas:
        for idx in u._by_role.get(f.rol, ()):
            if f.viola(u.facts[idx]):
                violaciones += 1
    return violaciones


def barrido_ingenuo(u, formas):
    """A demanda, sin índice: recorre el grafo entero por cada forma."""
    violaciones = 0
    for f in formas:
        for hecho in u.facts:
            if hecho.role == f.rol and f.viola(hecho):
                violaciones += 1
    return violaciones


print("=" * 74)
print("1 · LÍNEA BASE — escribir hechos hoy")
print("=" * 74)
base = {}
for n in ESCALAS:
    t = cronometrar(lambda n=n: universo(n))
    base[n] = t
    print(f"  {n:>7,} hechos: {t*1000:8.1f} ms   ({t/n*1e6:6.2f} µs por hecho)")

print()
print("=" * 74)
print("2 · A DEMANDA — barrido de restricciones sobre el universo ya escrito")
print("=" * 74)
for n in ESCALAS:
    u = universo(n)
    t_idx = cronometrar(lambda u=u: barrido_indexado(u, FORMAS), 5)
    t_ing = cronometrar(lambda u=u: barrido_ingenuo(u, FORMAS), 5)
    alcanzados = sum(len(u._by_role.get(f.rol, ())) for f in FORMAS)
    print(f"  {n:>7,} hechos · {alcanzados:>6,} alcanzados por las formas")
    print(f"        indexado: {t_idx*1000:7.2f} ms   ({t_idx/n*1e6:5.2f} µs por hecho del grafo)")
    print(f"        ingenuo:  {t_ing*1000:7.2f} ms   ({t_ing/t_idx:4.1f}× más lento)")

print()
print("=" * 74)
print("3 · AL ESCRIBIR — coste añadido a cada assert_fact")
print("=" * 74)


def universo_validando(n_hechos, formas):
    """Igual que universo(), pero comprobando las formas en cada escritura."""
    por_rol = {}
    for f in formas:
        por_rol.setdefault(f.rol, []).append(f)
    u = Universe(catalog=Catalog())
    roles = ["disponibilidad", "monto", "estado", "lugar_de", "momento"]
    violaciones = 0
    for i in range(n_hechos):
        s = Individual(id=f"sit_{i}", axis=Axis.O)
        rol = roles[i % len(roles)]
        v = _valor(rol, i)
        hecho = u.assert_fact(s, rol, v)
        for f in por_rol.get(rol, ()):          # indexado por rol
            if f.viola(hecho):
                violaciones += 1
    return u


for n in ESCALAS:
    t = cronometrar(lambda n=n: universo_validando(n, FORMAS))
    sobrecoste = (t - base[n]) / base[n] * 100
    print(f"  {n:>7,} hechos: {t*1000:8.1f} ms   "
          f"(+{sobrecoste:5.1f}% sobre la línea base)")

print()
print("  Con 50 formas en el catálogo, indexadas por rol:")
for n in ESCALAS:
    t = cronometrar(lambda n=n: universo_validando(n, FORMAS_MUCHAS))
    sobrecoste = (t - base[n]) / base[n] * 100
    print(f"  {n:>7,} hechos: {t*1000:8.1f} ms   "
          f"(+{sobrecoste:5.1f}% sobre la línea base)")

print()
print("=" * 74)
print("4 · EL CONTEXTO QUE IMPORTA")
print("=" * 74)
u = universo(100_000)
t_barrido = cronometrar(lambda: barrido_indexado(u, FORMAS), 5)
print(f"  Barrido completo de 100.000 hechos: {t_barrido*1000:.2f} ms")
print(f"  Un turno de LLM ronda los 2.000 ms.")
print(f"  El barrido es el {t_barrido*1000/2000*100:.3f}% de un turno de modelo.")


print()
print("=" * 74)
print("5 · LAS CLASES CARAS — no toda restricción cuesta lo mismo")
print("=" * 74)


def sweep_por_hecho(u):
    """Rango sobre un valor. Toca un hecho a la vez."""
    return sum(1 for f in FORMAS for i in u._by_role.get(f.rol, ())
               if f.viola(u.facts[i]))


def sweep_cardinalidad(u):
    """«Toda extracción tiene exactamente un agente.» Agrupa por sujeto."""
    conteo = {}
    for i in u._by_role.get("disponibilidad", ()):
        conteo[u.facts[i].subject.id] = conteo.get(u.facts[i].subject.id, 0) + 1
    return sum(1 for c in conteo.values() if c != 1)


def sweep_unicidad(u):
    """«Ningún valor de monto se repite.» Cruza todo el rol contra sí mismo."""
    vistos, dup = set(), 0
    for i in u._by_role.get("monto", ()):
        k = u.facts[i].value.id
        if k in vistos:
            dup += 1
        vistos.add(k)
    return dup


def sweep_relacional(u):
    """«Todo lo que tiene monto debe tener lugar.» Cruza dos roles por sujeto."""
    con_monto = {u.facts[i].subject.id for i in u._by_role.get("monto", ())}
    con_lugar = {u.facts[i].subject.id for i in u._by_role.get("lugar_de", ())}
    return len(con_monto - con_lugar)


for n in ESCALAS:
    u = universo(n)
    print(f"  {n:>7,} hechos:")
    for nombre, fn in (("rango (por hecho)", sweep_por_hecho),
                       ("cardinalidad (por sujeto)", sweep_cardinalidad),
                       ("unicidad (por rol)", sweep_unicidad),
                       ("relacional (dos roles)", sweep_relacional)):
        t = cronometrar(lambda fn=fn, u=u: fn(u), 5)
        print(f"        {nombre:<28} {t*1000:7.2f} ms")
