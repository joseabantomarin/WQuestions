"""Formas: lo que un hecho no debería violar.

La signatura tipada (D2) comprueba que un cable enchufe donde debe: que el
sujeto venga del eje correcto y el valor vaya al eje correcto. No dice nada
sobre el valor mismo. Una disponibilidad del 140 % encaja en la signatura tan
bien como una del 94 %.

La forma es la hermana de la signatura. Si la signatura dice qué enchufe
encaja, la forma dice qué voltaje es aceptable.

Dos cosas que este módulo NO hace, y por decisión:

- No rechaza nada. El almacén es de mundo abierto y así debe seguir: es lo que
  permite modelar cualquier dominio sin un comité que apruebe cada concepto.
- No lanza excepciones ante una violación. La violación se registra como un
  hecho más, con su vigencia y su estado, y se cierra cuando el hecho que la
  causaba se corrige. Una violación es un hecho sobre un hecho.

Las formas, como las reglas de derivación, son entidades del grafo:

    (forma_disponibilidad, tipo_forma,   rango)
    (forma_disponibilidad, rol_objetivo, "disponibilidad")
    (forma_disponibilidad, minimo,       0 K:Porcentaje)
    (forma_disponibilidad, maximo,       100 K:Porcentaje)
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Optional

from .axes import Axis
from .individual import Individual
from .magnitud import ErrorDimensional, Magnitud

# Roles con que una forma se describe a sí misma.
ROL_TIPO = "tipo_forma"
ROL_OBJETIVO = "rol_objetivo"
ROL_MINIMO = "minimo"
ROL_MAXIMO = "maximo"
ROL_REQUIERE = "rol_requerido"
ROL_TIPO_SUJETO = "aplica_a"

# Roles con que se registra una violación.
ROL_SOBRE = "sobre"
ROL_DETALLE = "detalle"
ROL_ESTADO = "estado"
ROL_JUSTIFICADO_POR = "justificado_por"

TIPOS = ("rango", "cardinalidad", "requiere", "unicidad")

CAT_FORMA = "forma_de_validacion"
CAT_VIOLACION = "violacion_de_forma"
EST_ABIERTA = "violacion_abierta"
EST_RESUELTA = "violacion_resuelta"


class ErrorDeForma(Exception):
    """La forma está mal declarada, o no se puede aplicar a lo que alcanza.

    Distinto de una violación: una violación es un dato del dominio; esto es
    un error del modelador.
    """


@dataclass(frozen=True)
class Violacion:
    """Lo que el evaluador encontró. Se convierte en hechos al registrarse."""

    forma_id: str
    sujeto_id: str
    detalle: str

    @property
    def clave(self) -> tuple:
        return (self.forma_id, self.sujeto_id)

    def __str__(self) -> str:
        return f"{self.sujeto_id}: {self.detalle} (por {self.forma_id})"


# ---------------------------------------------------------------------------
# Declarar formas
# ---------------------------------------------------------------------------

def declarar_forma(universe, forma_id: str, *, tipo: str, rol: str,
                   label: Optional[str] = None,
                   minimo: Optional[Individual] = None,
                   maximo: Optional[Individual] = None,
                   requiere: Optional[str] = None,
                   aplica_a: Optional[str] = None) -> Individual:
    """Crea una forma en O y le cuelga lo que comprueba."""
    if tipo not in TIPOS:
        raise ErrorDeForma(
            f"Tipo de forma desconocido: '{tipo}'. Los tipos son {TIPOS}.")

    # Declarar una forma escribe hechos, pero no son dato de dominio: si el
    # gancho de escritura estuviera activo intentaría evaluar la forma a medio
    # construir.
    universe._en_evaluacion = True
    try:
        return _declarar(universe, forma_id, tipo, rol, label, minimo, maximo,
                         requiere, aplica_a)
    finally:
        universe._en_evaluacion = False


def _declarar(universe, forma_id, tipo, rol, label, minimo, maximo,
              requiere, aplica_a) -> Individual:
    forma = universe.add_individual(Individual(
        id=forma_id, axis=Axis.O, label=label or forma_id))
    universe.assert_fact(forma, "instancia_de",
                         _cat(universe, CAT_FORMA))
    universe.assert_fact(forma, ROL_TIPO, _cat(universe, tipo))
    universe.assert_fact(forma, ROL_OBJETIVO, _texto(universe, rol))

    if tipo == "rango":
        if minimo is None and maximo is None:
            raise ErrorDeForma(
                f"La forma de rango '{forma_id}' no acota nada: dale un "
                f"mínimo, un máximo o los dos.")
        if minimo is not None:
            universe.assert_fact(forma, ROL_MINIMO, minimo)
        if maximo is not None:
            universe.assert_fact(forma, ROL_MAXIMO, maximo)

    if tipo == "cardinalidad":
        if minimo is None and maximo is None:
            raise ErrorDeForma(
                f"La forma de cardinalidad '{forma_id}' no acota nada.")
        if minimo is not None:
            universe.assert_fact(forma, ROL_MINIMO, minimo)
        if maximo is not None:
            universe.assert_fact(forma, ROL_MAXIMO, maximo)

    if tipo == "requiere":
        if requiere is None:
            raise ErrorDeForma(
                f"La forma '{forma_id}' es de tipo requiere y no dice qué rol "
                f"exige.")
        universe.assert_fact(forma, ROL_REQUIERE, _texto(universe, requiere))

    if aplica_a is not None:
        universe.assert_fact(forma, ROL_TIPO_SUJETO, _cat(universe, aplica_a))

    return forma


def _cat(universe, cat_id: str) -> Individual:
    return universe.add_individual(Individual(id=cat_id, axis=Axis.K,
                                              label=cat_id))


def _texto(universe, texto: str) -> Individual:
    """Un literal de texto vive en K, como la expresión de una regla."""
    return universe.add_individual(Individual(
        id=f"txt_{texto}", axis=Axis.K, label=texto))


# ---------------------------------------------------------------------------
# Leer una forma del grafo
# ---------------------------------------------------------------------------

@dataclass
class _FormaLeida:
    id: str
    tipo: str
    rol: str
    minimo: Optional[Individual] = None
    maximo: Optional[Individual] = None
    requiere: Optional[str] = None
    aplica_a: Optional[str] = None


def _leer_forma(universe, forma: Individual) -> _FormaLeida:
    hechos: Dict[str, Individual] = {}
    for f in universe.facts_about(forma):
        hechos[f.role] = f.value
    if ROL_TIPO not in hechos or ROL_OBJETIVO not in hechos:
        raise ErrorDeForma(
            f"'{forma.id}' no declara tipo_forma y rol_objetivo; no es una forma.")
    return _FormaLeida(
        id=forma.id,
        tipo=hechos[ROL_TIPO].id,
        rol=hechos[ROL_OBJETIVO].label or hechos[ROL_OBJETIVO].id,
        minimo=hechos.get(ROL_MINIMO),
        maximo=hechos.get(ROL_MAXIMO),
        requiere=(hechos[ROL_REQUIERE].label if ROL_REQUIERE in hechos else None),
        aplica_a=(hechos[ROL_TIPO_SUJETO].id if ROL_TIPO_SUJETO in hechos else None),
    )


def formas_declaradas(universe) -> List[Individual]:
    """Todas las formas del universo, en orden de declaración."""
    return [f.subject for f in universe.facts
            if f.role == "instancia_de" and f.value.id == CAT_FORMA]


# ---------------------------------------------------------------------------
# Evaluar
# ---------------------------------------------------------------------------

def _hechos_del_rol(universe, rol: str, momento: Optional[datetime],
                    colapsar: bool = True):
    """Los hechos del rol que hay que evaluar, en el momento dado.

    Dos matices que el modelo ya tenía resueltos y aquí se cobran:

    - **Vigencia (D6).** Solo se evalúa lo que rige en `momento`. Un escenario
      proyectado a julio se valida pasando julio, no hoy.
    - **Cardinalidad (D2).** Si la signatura dice que el rol es funcional, el
      sujeto tiene un solo valor y el que cuenta es el último: así una
      corrección apaga la violación en vez de acumularla. Si es múltiple, se
      evalúan todos. Un rol no declarado se trata como funcional, que es como
      lo resuelve el resto del sistema.
    """
    hechos = [universe.facts[i] for i in universe._by_role.get(rol, ())]
    if momento is not None:
        hechos = [h for h in hechos if h.is_valid_at(momento)]

    if not colapsar:
        return hechos

    multiple = False
    if universe.catalog is not None:
        sig = universe.catalog.get(rol)
        multiple = sig is not None and not sig.functional
    if multiple:
        return hechos

    ultimo_por_sujeto = {}
    for h in hechos:
        ultimo_por_sujeto[h.subject.id] = h
    return list(ultimo_por_sujeto.values())


def _es_del_tipo(universe, sujeto: Individual, tipo_id: Optional[str]) -> bool:
    if tipo_id is None:
        return True
    return any(f.role == "instancia_de" and f.value.id == tipo_id
               for f in universe.facts_about(sujeto))


def _comparar(universe, valor: Individual, cota: Individual):
    """Compara dos magnitudes respetando unidades. Devuelve -1, 0 o 1."""
    try:
        a = Magnitud.de(universe, valor)
        b = Magnitud.de(universe, cota)
    except ErrorDimensional as e:
        raise ErrorDeForma(f"No se pudo comparar: {e}") from e
    if a._reducida.exponentes != b._reducida.exponentes:
        raise ErrorDeForma(
            f"La cota está en {b.dimension} y el valor en {a.dimension}: "
            f"la forma no es aplicable a este hecho.")
    return (a.valor_base > b.valor_base) - (a.valor_base < b.valor_base)


def _evaluar_rango(universe, fl: _FormaLeida, momento=None) -> List[Violacion]:
    out = []
    for hecho in _hechos_del_rol(universe, fl.rol, momento):
        if not _es_del_tipo(universe, hecho.subject, fl.aplica_a):
            continue
        if fl.minimo is not None and _comparar(universe, hecho.value, fl.minimo) < 0:
            out.append(Violacion(fl.id, hecho.subject.id,
                                 f"{_n(hecho.value)} por debajo del mínimo "
                                 f"{_n(fl.minimo)}"))
        elif fl.maximo is not None and _comparar(universe, hecho.value, fl.maximo) > 0:
            out.append(Violacion(fl.id, hecho.subject.id,
                                 f"{_n(hecho.value)} por encima del máximo "
                                 f"{_n(fl.maximo)}"))
    return out


def _evaluar_cardinalidad(universe, fl: _FormaLeida, momento=None) -> List[Violacion]:
    conteo: Dict[str, int] = {}
    sujetos: Dict[str, Individual] = {}
    # Contar ocurrencias exige verlas todas: colapsar al valor vigente daría
    # siempre uno y la forma no comprobaría nada.
    for hecho in _hechos_del_rol(universe, fl.rol, momento, colapsar=False):
        s = hecho.subject
        if not _es_del_tipo(universe, s, fl.aplica_a):
            continue
        conteo[s.id] = conteo.get(s.id, 0) + 1
        sujetos[s.id] = s
    out = []
    for sid, c in conteo.items():
        if fl.minimo is not None and c < _valor(fl.minimo):
            out.append(Violacion(fl.id, sid,
                                 f"tiene {c} '{fl.rol}' y el mínimo es "
                                 f"{_valor(fl.minimo):g}"))
        elif fl.maximo is not None and c > _valor(fl.maximo):
            out.append(Violacion(fl.id, sid,
                                 f"tiene {c} '{fl.rol}' y el máximo es "
                                 f"{_valor(fl.maximo):g}"))
    return out


def _evaluar_requiere(universe, fl: _FormaLeida, momento=None) -> List[Violacion]:
    con_rol = {}
    for hecho in _hechos_del_rol(universe, fl.rol, momento):
        if _es_del_tipo(universe, hecho.subject, fl.aplica_a):
            con_rol[hecho.subject.id] = hecho.subject
    con_requerido = {h.subject.id
                     for h in _hechos_del_rol(universe, fl.requiere, momento)}
    return [Violacion(fl.id, sid,
                      f"tiene '{fl.rol}' y le falta '{fl.requiere}'")
            for sid in con_rol if sid not in con_requerido]


def _evaluar_unicidad(universe, fl: _FormaLeida, momento=None) -> List[Violacion]:
    visto: Dict[str, str] = {}
    out = []
    for hecho in _hechos_del_rol(universe, fl.rol, momento):
        if not _es_del_tipo(universe, hecho.subject, fl.aplica_a):
            continue
        clave = hecho.value.id
        if clave in visto and visto[clave] != hecho.subject.id:
            out.append(Violacion(
                fl.id, hecho.subject.id,
                f"repite '{fl.rol}' = {clave}, ya usado por {visto[clave]}"))
        else:
            visto.setdefault(clave, hecho.subject.id)
    return out


_EVALUADORES = {
    "rango": _evaluar_rango,
    "cardinalidad": _evaluar_cardinalidad,
    "requiere": _evaluar_requiere,
    "unicidad": _evaluar_unicidad,
}


def _n(ind: Individual):
    p = ind.payload
    if isinstance(p, dict) and "value" in p:
        return f"{p['value']:g} {p.get('unit', '')}".strip()
    return ind.label or ind.id


def _valor(ind: Individual) -> float:
    p = ind.payload
    if not isinstance(p, dict) or "value" not in p:
        raise ErrorDeForma(f"'{ind.id}' debería ser una magnitud y no lo es.")
    return float(p["value"])


def evaluar_formas(universe, solo: Optional[List[str]] = None,
                   momento: Optional[datetime] = None) -> List[Violacion]:
    """Comprueba las formas y devuelve lo que encontró. No escribe nada.

    `momento` fija en qué instante se mira el grafo: por omisión, ahora. Pasar
    una fecha futura valida un escenario proyectado en la fecha en la que
    regiría, que es la única en la que tiene sentido juzgarlo.
    """
    momento = momento or datetime.now(timezone.utc)
    out: List[Violacion] = []
    for forma in formas_declaradas(universe):
        if solo is not None and forma.id not in solo:
            continue
        fl = _leer_forma(universe, forma)
        out.extend(_EVALUADORES[fl.tipo](universe, fl, momento))
    return out


# ---------------------------------------------------------------------------
# Registrar: la violación como hecho
# ---------------------------------------------------------------------------

def _violaciones_registradas(universe) -> Dict[tuple, Individual]:
    """Las violaciones ya escritas en el grafo, por (forma, sujeto)."""
    out = {}
    for f in universe.facts:
        if f.role == "instancia_de" and f.value.id == CAT_VIOLACION:
            hechos = {g.role: g.value for g in universe.facts_about(f.subject)}
            clave = (hechos.get(ROL_JUSTIFICADO_POR, f.subject).id,
                     hechos.get(ROL_SOBRE, f.subject).id)
            out[clave] = f.subject
    return out


def _estado_actual(universe, violacion: Individual, momento: datetime) -> Optional[str]:
    estados = [f for f in universe.facts_about(violacion, at=momento)
               if f.role == ROL_ESTADO]
    return estados[-1].value.id if estados else None


def registrar_violaciones(universe, violaciones: List[Violacion],
                          momento: Optional[datetime] = None,
                          formas_evaluadas: Optional[List[str]] = None) -> dict:
    """Abre las violaciones nuevas y cierra las que dejaron de serlo.

    Nada se borra: cerrar es añadir un estado con su vigencia, igual que un
    punchitem que pasa de abierto a cerrado en el capítulo 23.
    """
    momento = momento or datetime.now(timezone.utc)
    universe._en_evaluacion = True
    try:
        registradas = _violaciones_registradas(universe)
        vivas = {v.clave: v for v in violaciones}
        abiertas, cerradas = [], []

        for clave, v in vivas.items():
            existente = registradas.get(clave)
            if existente is None:
                nodo = universe.add_individual(Individual(
                    id=f"violacion_{len(registradas) + len(abiertas) + 1:04d}",
                    axis=Axis.O, label=v.detalle))
                universe.assert_fact(nodo, "instancia_de",
                                     _cat(universe, CAT_VIOLACION))
                universe.assert_fact(nodo, ROL_SOBRE,
                                     universe.ind(v.sujeto_id))
                universe.assert_fact(nodo, ROL_JUSTIFICADO_POR,
                                     universe.ind(v.forma_id))
                universe.assert_fact(nodo, ROL_DETALLE,
                                     _texto(universe, v.detalle))
                universe.assert_fact(nodo, ROL_ESTADO,
                                     _cat(universe, EST_ABIERTA),
                                     valid_from=momento)
                abiertas.append(nodo.id)
            elif _estado_actual(universe, existente, momento) == EST_RESUELTA:
                universe.assert_fact(existente, ROL_ESTADO,
                                     _cat(universe, EST_ABIERTA),
                                     valid_from=momento)
                abiertas.append(existente.id)

        for clave, nodo in registradas.items():
            # Solo se cierran violaciones de las formas que se acaban de
            # evaluar: un barrido parcial no puede opinar sobre las demás.
            if formas_evaluadas is not None and clave[0] not in formas_evaluadas:
                continue
            if clave not in vivas and \
                    _estado_actual(universe, nodo, momento) == EST_ABIERTA:
                universe.assert_fact(nodo, ROL_ESTADO,
                                     _cat(universe, EST_RESUELTA),
                                     valid_from=momento)
                cerradas.append(nodo.id)

        return {"abiertas": abiertas, "cerradas": cerradas,
                "vigentes": len(vivas)}
    finally:
        universe._en_evaluacion = False
