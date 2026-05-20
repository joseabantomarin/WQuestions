# Anexo — El prototipo en Python: librería núcleo

Este anexo contiene el **código fuente íntegro de la librería núcleo** del prototipo de WQuestions (~850 líneas). Es lo que da cuerpo a las afirmaciones del libro: las ocho coordenadas, los hechos atómicos con signatura, las situaciones reificadas, el catálogo canónico de roles, el lexicon con resolución de polisemia, la bitemporalidad y el motor de consulta — todo cabe en nueve archivos cortos.

> **Importante.** Este anexo es deliberadamente parcial: incluye **solo la librería núcleo** (`prototipo/wq/`). Los **ejemplos por dominio** (sauna, taxi, clínica, banco, dominios previos), los **tests** completos del modelo y los scripts de utilidad **no aparecen acá**, pero existen y son ejecutables. El proyecto completo, con todo lo que la Parte V ejercita, está publicado en el repositorio:
>
> **https://github.com/joseabantomarin/WQuestions**
>
> Quien quiera correr los ocho dominios, ver los tests pasando o extender el modelo encontrará en el repo todo lo que el libro afirma — incluyendo lo que este anexo no muestra.

## La arquitectura en una sola mirada

El prototipo se organiza en nueve módulos que se apilan como capas:

```
                  ┌─────────────────────────────┐
                  │      __init__.py            │  Superficie pública
                  └─────────────────────────────┘
                                │
                  ┌─────────────────────────────┐
                  │       ingest.py             │  Pipeline de ingesta
                  └─────────────────────────────┘
                                │
                  ┌─────────────────────────────┐
                  │       query.py              │  Motor de consulta
                  └─────────────────────────────┘
                                │
                  ┌─────────────────────────────┐
                  │      universe.py            │  Container con índices
                  └─────────────────────────────┘
                                │
        ┌───────────────────────┴───────────────────────┐
        │                                               │
┌───────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  catalog.py   │  │   lexicon.py    │  │     fact.py     │
│  (D8: roles)  │  │  (D9: verbos)   │  │  (D3: tripleta) │
└───────────────┘  └─────────────────┘  └─────────────────┘
        │                  │                     │
        └─────────┬────────┴─────────────────────┘
                  │
        ┌───────────────────────┐
        │    individual.py       │  Individuos en los ejes
        └───────────────────────┘
                  │
        ┌───────────────────────┐
        │      axes.py           │  Los ocho ejes
        └───────────────────────┘
```

El orden de lectura natural va de abajo hacia arriba: primero los ejes (la base), luego cómo se ven los individuos, luego los hechos, luego las dos estructuras transversales (catálogo y lexicon), luego el universo que los contiene, y finalmente la API de ingesta y consulta. Las nueve secciones de este anexo siguen ese orden.

---

## §A1 — `axes.py` — los ocho ejes

35 líneas. Es la pieza fundacional. Declara los seis ejes de valor (Q, O, L, T, N, K) y los dos ejes estructurales (P, M) como un `Enum`. Todo el resto del modelo se referencia contra estos identificadores.

```python
"""Los 8 ejes de WQuestions.

Seis ejes de valor (contienen individuos):
    Q — quién — agentes
    O — qué  — objetos / situaciones reificadas
    L — dónde — lugares
    T — cuándo — momentos / intervalos
    N — cuánto — magnitudes con unidad
    K — clase — categorías atemporales

Dos ejes estructurales (contienen etiquetas con signatura):
    P — predicados funcionales (un valor por sujeto)
    M — predicados no funcionales (varios valores admitidos)
"""

from enum import Enum


class Axis(Enum):
    Q = "Q"  # quien
    O = "O"  # qué (objectum)
    L = "L"  # dónde
    T = "T"  # cuándo (tempus)
    N = "N"  # cuánto
    K = "K"  # clase
    P = "P"  # cuál (funcional)
    M = "M"  # cómo / multi (modus)


VALUE_AXES = {Axis.Q, Axis.O, Axis.L, Axis.T, Axis.N, Axis.K}
PREDICATE_AXES = {Axis.P, Axis.M}


def is_value_axis(axis: Axis) -> bool:
    return axis in VALUE_AXES
```

---

## §A2 — `individual.py` — individuos en los ejes

81 líneas. Define qué es un *individuo* — la entidad que vive en alguno de los seis ejes de valor — y cómo se construyen los individuos primitivos (un instante temporal `time_point`, una magnitud con unidad `quantity`, una categoría `category`). El `mint_id` genera identificadores cortos y monótonos: en producción se reemplaza por UUID v7.

```python
"""Individuos del modelo: instancias de cualquier eje de valor.

Cada individuo tiene un identificador estable y vive en uno y solo un eje.
Para sujetos sintéticos usamos un mint determinista (id corto, monótono)
en vez de UUID — la observabilidad gana, la pérdida de globalidad no
importa para un prototipo.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Any, Dict
from itertools import count

from .axes import Axis, is_value_axis


_counter = count(1)


def mint_id(prefix: str = "id") -> str:
    """Genera un id corto y monótono. En producción se reemplazaría por UUID v7."""
    n = next(_counter)
    return f"{prefix}_{n:06d}"


@dataclass(frozen=True)
class Individual:
    """Individuo en un eje de valor.

    `payload` permite alojar valores nativos cuando el "individuo" es en
    realidad un dato (un instante T, una magnitud N, una categoría K). Para
    Q y O suele ser None; el id basta.
    """

    id: str
    axis: Axis
    label: Optional[str] = None
    payload: Any = None
    meta: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not is_value_axis(self.axis):
            raise ValueError(
                f"Un individuo debe vivir en un eje de valor, no en {self.axis}."
            )

    def __repr__(self) -> str:
        tag = self.label or self.id
        return f"<{self.axis.value}:{tag}>"


# --- helpers para individuos "primitivos" -----------------------------------


def time_point(iso: str) -> Individual:
    """Crea un individuo T desde una marca ISO 8601."""
    from datetime import datetime
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    except ValueError as e:
        raise ValueError(f"Marca temporal inválida: {iso}") from e
    return Individual(id=f"t_{iso}", axis=Axis.T, label=iso, payload=dt)


def quantity(value: float, unit_k: "Individual") -> Individual:
    """Crea un individuo N con valor numérico y unidad anclada en K."""
    if unit_k.axis != Axis.K:
        raise ValueError(
            f"La unidad debe vivir en K (recibido: {unit_k.axis})."
        )
    return Individual(
        id=mint_id("n"),
        axis=Axis.N,
        label=f"{value} {unit_k.label or unit_k.id}",
        payload={"value": value, "unit": unit_k.id},
    )


def category(label: str) -> Individual:
    """Crea un individuo K (categoría) con id derivado del label."""
    return Individual(id=label, axis=Axis.K, label=label)
```

---

## §A3 — `fact.py` — el hecho atómico (D3) con bitemporalidad (D6)

61 líneas. La unidad mínima del modelo. Cada hecho es una tupla inmutable `(sujeto, rol, valor)` con un rango de vigencia opcional `[valid_from, valid_to)` y un `tx_time` para auditoría. El método `is_valid_at` implementa la lógica de D6: si no hay vigencia, el hecho es atemporal; si la hay, se verifica que el momento solicitado caiga en el intervalo.

```python
"""Hechos atómicos: la unidad mínima del modelo.

Cada hecho es una tupla `(sujeto, rol, valor)` donde:
- `sujeto` y `valor` son `Individual` (viven en algún eje de valor).
- `rol` es una etiqueta del catálogo canónico (D8) o de su capa lexicon.

D6 — vigencia temporal: cada hecho lleva opcionalmente un rango
`[valid_from, valid_to)` que indica desde cuándo y hasta cuándo es cierto en
el mundo. Si `valid_to is None`, está abierto al futuro.

Adicionalmente registramos `tx_time` (transaction time): el momento en el que
el hecho entró al sistema. Esto da bitemporalidad ligera, suficiente para
auditoría.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from .individual import Individual


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class Fact:
    subject: Individual
    role: str
    value: Individual
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    tx_time: datetime = field(default_factory=_utcnow)

    def is_valid_at(self, moment: datetime) -> bool:
        """¿Este hecho es cierto en el mundo en `moment`?

        Reglas:
        - Si no hay vigencia, el hecho es atemporal: vale siempre.
        - `valid_from` inclusivo, `valid_to` exclusivo.
        - `valid_to is None` significa "abierto al futuro".
        """
        if self.valid_from is None and self.valid_to is None:
            return True
        if self.valid_from is not None and moment < self.valid_from:
            return False
        if self.valid_to is not None and moment >= self.valid_to:
            return False
        return True

    def __repr__(self) -> str:
        s = self.subject.label or self.subject.id
        v = self.value.label or self.value.id
        base = f"({s}, {self.role}, {v})"
        if self.valid_from or self.valid_to:
            f = self.valid_from.isoformat() if self.valid_from else "-∞"
            t = self.valid_to.isoformat() if self.valid_to else "+∞"
            base += f"  [{f} .. {t})"
        return base
```

---

## §A4 — `catalog.py` — el catálogo canónico de roles (D8)

179 líneas. Es el módulo más largo de la librería núcleo y donde se materializa D8: declara los 38 roles canónicos con su signatura tipada (`dominio → rango`) y la validación mecánica que verifica que cada hecho respete las signaturas. La política liberal (un rol no declarado se acepta sin validar) está implementada en el método `validate`.

```python
"""Catálogo canónico de roles (D8).

Cada rol declara una signatura tipada `dominio → rango`, ambos ejes,
más si es **funcional** (un valor por sujeto: vive en P) o **multi-valor**
(vive en M). La signatura habilita la validación mecánica de hechos:
al insertar `(s, role, v)` el catálogo verifica que `s.axis` coincida con
el dominio y `v.axis` con el rango.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Optional

from .axes import Axis
from .individual import Individual


@dataclass(frozen=True)
class RoleSignature:
    name: str
    domain: Axis    # eje del sujeto
    range: Axis     # eje del valor
    functional: bool  # True → P (una por sujeto), False → M (multi)
    description: str = ""


class SignatureError(ValueError):
    pass


class Catalog:
    """Catálogo de signaturas canónicas + validación de hechos."""

    def __init__(self):
        self._roles: Dict[str, RoleSignature] = {}
        self._load_canonical()

    def register(self, sig: RoleSignature) -> None:
        if sig.name in self._roles:
            existing = self._roles[sig.name]
            if existing != sig:
                raise SignatureError(
                    f"Rol '{sig.name}' ya registrado con signatura distinta: "
                    f"{existing} vs {sig}"
                )
            return
        self._roles[sig.name] = sig

    def get(self, name: str) -> Optional[RoleSignature]:
        return self._roles.get(name)

    def validate(self, role: str, subject: Individual, value: Individual) -> None:
        """Lanza `SignatureError` si el hecho viola la signatura."""
        sig = self._roles.get(role)
        if sig is None:
            # Rol no declarado: política liberal — se permite, no se valida.
            # Una política estricta lo rechazaría; preferimos extensibilidad.
            return
        if subject.axis != sig.domain:
            raise SignatureError(
                f"Sujeto en eje incorrecto para '{role}': se esperaba "
                f"{sig.domain.value}, recibido {subject.axis.value} "
                f"(sujeto={subject})"
            )
        if value.axis != sig.range:
            raise SignatureError(
                f"Valor en eje incorrecto para '{role}': se esperaba "
                f"{sig.range.value}, recibido {value.axis.value} "
                f"(valor={value})"
            )

    def __contains__(self, name: str) -> bool:
        return name in self._roles

    def __len__(self) -> int:
        return len(self._roles)

    # ------------------------------------------------------------------
    # Carga del catálogo canónico (subset del documento WQuestions.md)
    # ------------------------------------------------------------------

    def _load_canonical(self) -> None:
        canonical = [
            # --- estructurales ---
            RoleSignature("instancia_de", Axis.O, Axis.K, False,
                          "sujeto pertenece a la categoría"),
            RoleSignature("subtipo_de", Axis.K, Axis.K, False,
                          "subtipo conceptual"),
            RoleSignature("parte_de", Axis.O, Axis.O, False,
                          "subobjeto/subevento de"),
            RoleSignature("contiene", Axis.O, Axis.O, False,
                          "inversa de parte_de"),

            # --- participantes (Q es típico) ---
            RoleSignature("agente", Axis.O, Axis.Q, True,
                          "agente principal de la situación"),
            RoleSignature("paciente", Axis.O, Axis.Q, True,
                          "afectado por la situación"),
            RoleSignature("tema", Axis.O, Axis.O, True,
                          "objeto temático (cosa o sub-situación)"),
            RoleSignature("beneficiario", Axis.O, Axis.Q, True,
                          "destinatario o beneficiario"),
            RoleSignature("experimentador", Axis.O, Axis.Q, True,
                          "quien experimenta un estado mental"),
            RoleSignature("instrumento", Axis.O, Axis.O, True,
                          "objeto usado para ejecutar la acción"),
            RoleSignature("comprador", Axis.O, Axis.Q, True,
                          "comprador en una venta"),
            RoleSignature("cliente", Axis.O, Axis.Q, True,
                          "cliente de un servicio (alias frecuente de agente)"),

            # --- lugar / tiempo ---
            RoleSignature("lugar_de", Axis.O, Axis.L, True,
                          "lugar donde ocurre la situación"),
            RoleSignature("origen", Axis.O, Axis.L, True,
                          "lugar de origen"),
            RoleSignature("destino", Axis.O, Axis.L, True,
                          "lugar de destino"),
            RoleSignature("lugar_destino", Axis.O, Axis.L, True,
                          "alias de destino"),
            RoleSignature("momento", Axis.O, Axis.T, True,
                          "momento puntual"),
            RoleSignature("inicio", Axis.O, Axis.T, True,
                          "instante de inicio"),
            RoleSignature("fin", Axis.O, Axis.T, True,
                          "instante de fin"),

            # --- cuantitativos ---
            RoleSignature("monto", Axis.O, Axis.N, True,
                          "cantidad numérica con unidad"),
            RoleSignature("cantidad", Axis.O, Axis.N, True,
                          "alias de monto"),
            RoleSignature("por_cuanto", Axis.O, Axis.N, True,
                          "precio o medida asociada"),
            RoleSignature("unidad", Axis.O, Axis.K, True,
                          "unidad de medida (QUDT)"),

            # --- clasificatorios ---
            RoleSignature("estatus_factual", Axis.O, Axis.K, True,
                          "real / intencionado / no_realizable / ..."),
            RoleSignature("modalidad", Axis.O, Axis.K, True,
                          "volitiva / deóntica / alética / epistémica"),
            RoleSignature("polaridad", Axis.O, Axis.K, True,
                          "afirmativa / negativa"),
            RoleSignature("calificacion", Axis.O, Axis.K, True,
                          "atributo cualitativo"),

            # --- "por qué" (D7, capítulo 11) ---
            RoleSignature("causado_por", Axis.O, Axis.O, False,
                          "causalidad mecánica"),
            RoleSignature("motivado_por", Axis.O, Axis.O, False,
                          "motivación intencional"),
            RoleSignature("con_finalidad", Axis.O, Axis.O, False,
                          "propósito"),
            RoleSignature("justificado_por", Axis.O, Axis.O, False,
                          "regla que autoriza"),

            # --- inter-situacionales ---
            RoleSignature("precede", Axis.O, Axis.O, False,
                          "orden lógico/temporal"),
            RoleSignature("sigue_a", Axis.O, Axis.O, False,
                          "inversa de precede"),
            RoleSignature("cumple", Axis.O, Axis.O, False,
                          "cumple una obligación"),
            RoleSignature("cancela", Axis.O, Axis.O, False,
                          "deja sin efecto"),
            RoleSignature("rectifica", Axis.O, Axis.O, False,
                          "corrige otra situación"),
            RoleSignature("contrasta_con", Axis.O, Axis.O, False,
                          "relación adversativa (\"pero\")"),

            # --- atributos del sujeto Q ---
            RoleSignature("nombre", Axis.Q, Axis.K, True,
                          "nombre de un agente"),
            RoleSignature("identificador", Axis.Q, Axis.K, True,
                          "id documental"),
        ]
        for sig in canonical:
            self.register(sig)
```

---

## §A5 — `lexicon.py` — el lexicon con resolución de polisemia (D9)

116 líneas. Implementa la capa de traducción entre el lenguaje natural del usuario y los roles canónicos. Cada `LexiconEntry` declara su `pattern` de complementos (que dispara la polisemia: `dar [la_mano]` vs `dar [conferencia]`) y la resolución elige la entrada **más específica** que coincida. También maneja dialectos de dominio y formas nominales.

```python
"""Lexicon: diccionario verbo → tipo de situación + roles + aliases.

Implementa el paradigma del capítulo 13: cada entrada declara una
signatura (qué roles obligatorios y opcionales), un tipo de situación en K,
y aliases naturales por rol y por dominio. La resolución de polisemia
elige la entrada más específica que coincide con el patrón de complemento.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class LexiconEntry:
    verb: str                          # "vender", "dar", ...
    situation_type: str                # K id, ej. "accion_vender"
    obligatory: List[str] = field(default_factory=list)
    optional: List[str] = field(default_factory=list)
    aliases: Dict[str, List[str]] = field(default_factory=dict)
    nominal_forms: List[str] = field(default_factory=list)
    pattern: Optional[Tuple[str, ...]] = None  # complementos clave para polisemia
    notes: str = ""
    example: str = ""

    def specificity(self) -> int:
        """Cuanto más largo el patrón, más específica la entrada."""
        return 0 if self.pattern is None else len(self.pattern)

    def matches(self, observed_complements: List[str]) -> bool:
        """¿Esta entrada coincide con los complementos vistos en la oración?

        Una entrada con `pattern=None` siempre coincide (entrada genérica).
        Una entrada con patrón coincide si TODOS sus elementos aparecen
        entre los complementos.
        """
        if self.pattern is None:
            return True
        obs = set(observed_complements)
        return all(p in obs for p in self.pattern)


class Lexicon:
    """Lexicon con resolución de polisemia.

    Las entradas se registran por verbo; varias entradas pueden compartir
    verbo (polisemia). `resolve(verb, complements)` devuelve la entrada
    más específica que coincide.
    """

    def __init__(self):
        self._by_verb: Dict[str, List[LexiconEntry]] = {}
        # Aliases globales de dominio: nombre_usuario → rol_canonico
        self._domain_aliases: Dict[str, Dict[str, str]] = {}
        # Aliases nominales globales: forma_nominal → verbo
        self._nominal_index: Dict[str, str] = {}

    # --- registro ----------------------------------------------------------

    def register(self, entry: LexiconEntry) -> None:
        self._by_verb.setdefault(entry.verb, []).append(entry)
        # Orden por especificidad decreciente: más específico primero.
        self._by_verb[entry.verb].sort(key=lambda e: -e.specificity())
        for nf in entry.nominal_forms:
            self._nominal_index[nf] = entry.verb

    def register_domain_dialect(self, domain: str,
                                aliases: Dict[str, str]) -> None:
        """Agrega un dialecto de dominio: nombre_usuario → rol_canónico."""
        self._domain_aliases.setdefault(domain, {}).update(aliases)

    # --- resolución --------------------------------------------------------

    def resolve(self, verb: str,
                complements: Optional[List[str]] = None) -> Optional[LexiconEntry]:
        """Devuelve la entrada más específica que coincide con el verbo
        y los complementos observados. None si no hay match.
        """
        candidates = self._by_verb.get(verb, [])
        comps = complements or []
        for entry in candidates:  # ya ordenadas más específico → más general
            if entry.matches(comps):
                return entry
        return None

    def resolve_nominal(self, nominal_form: str,
                        complements: Optional[List[str]] = None
                        ) -> Optional[LexiconEntry]:
        """Resolución por forma nominal (nominalización).

        *"la llegada del avión"* → verbo `llegar` → entrada de llegar.
        """
        verb = self._nominal_index.get(nominal_form)
        if verb is None:
            return None
        return self.resolve(verb, complements)

    def translate_alias(self, domain: str, user_term: str) -> Optional[str]:
        """Traduce un término de usuario al rol canónico vía dialecto."""
        return self._domain_aliases.get(domain, {}).get(user_term)

    def alias_for_role(self, verb: str, role: str) -> List[str]:
        """Aliases declarados para un rol de una entrada específica."""
        entries = self._by_verb.get(verb, [])
        for e in entries:
            if role in e.aliases:
                return e.aliases[role]
        return []

    # --- introspección -----------------------------------------------------

    def verbs(self) -> List[str]:
        return list(self._by_verb.keys())

    def entries_for(self, verb: str) -> List[LexiconEntry]:
        return list(self._by_verb.get(verb, []))
```

---

## §A6 — `universe.py` — el universo V

130 líneas. El container que aloja todos los individuos y todos los hechos, con tres índices (por sujeto, por valor, por rol) para que las consultas no degraden a barrido lineal. Aquí se conecta el catálogo: cada `assert_fact` delega la validación de signatura al catálogo si está inyectado. Los hechos son inmutables; nunca se sobreescriben — los cambios se modelan con vigencia temporal (D6) o con nuevas situaciones.

```python
"""El universo V — unión disjunta de los ejes de valor.

`Universe` es el almacenamiento en memoria del prototipo: una lista de
individuos y una lista de hechos, con índices para consulta eficiente.

Diseño:
- Se accede vía `add_individual`, `assert_fact`, `query`.
- La validación de signatura ocurre al insertar el hecho (delegada al Catalog).
- Los hechos son inmutables; "cambios" se modelan como nuevas situaciones
  o como rangos de vigencia (D6).

No persiste a disco — el prototipo es en memoria. Para tests y demos basta.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Iterator, Tuple, Any

from .axes import Axis
from .individual import Individual
from .fact import Fact


@dataclass
class Universe:
    name: str = "default"
    individuals: Dict[str, Individual] = field(default_factory=dict)
    facts: List[Fact] = field(default_factory=list)
    catalog: Any = None  # Catalog inyectado opcionalmente para validación

    # Índices
    _by_subject: Dict[str, List[int]] = field(default_factory=dict)
    _by_value: Dict[str, List[int]] = field(default_factory=dict)
    _by_role: Dict[str, List[int]] = field(default_factory=dict)

    # --- registro de individuos --------------------------------------------

    def add_individual(self, ind: Individual) -> Individual:
        existing = self.individuals.get(ind.id)
        if existing is not None:
            if existing.axis != ind.axis:
                raise ValueError(
                    f"Conflicto de eje para {ind.id}: ya existe en {existing.axis} "
                    f"y se intenta registrar en {ind.axis}."
                )
            return existing
        self.individuals[ind.id] = ind
        return ind

    def ind(self, id_or_label: str) -> Individual:
        """Recupera un individuo por id."""
        if id_or_label in self.individuals:
            return self.individuals[id_or_label]
        raise KeyError(f"Individuo no registrado: {id_or_label}")

    # --- afirmación de hechos ----------------------------------------------

    def assert_fact(
        self,
        subject: Individual,
        role: str,
        value: Individual,
        valid_from: Optional[datetime] = None,
        valid_to: Optional[datetime] = None,
    ) -> Fact:
        """Afirma un hecho atómico. Valida la signatura si hay catálogo."""
        self.add_individual(subject)
        self.add_individual(value)

        if self.catalog is not None:
            self.catalog.validate(role, subject, value)

        fact = Fact(
            subject=subject,
            role=role,
            value=value,
            valid_from=valid_from,
            valid_to=valid_to,
        )
        idx = len(self.facts)
        self.facts.append(fact)
        self._by_subject.setdefault(subject.id, []).append(idx)
        self._by_value.setdefault(value.id, []).append(idx)
        self._by_role.setdefault(role, []).append(idx)
        return fact

    # --- recuperación ------------------------------------------------------

    def facts_about(self, individual: Individual,
                    at: Optional[datetime] = None) -> List[Fact]:
        """Todos los hechos donde `individual` es el sujeto."""
        idxs = self._by_subject.get(individual.id, [])
        result = [self.facts[i] for i in idxs]
        if at is not None:
            result = [f for f in result if f.is_valid_at(at)]
        return result

    def facts_with_role(self, role: str,
                        at: Optional[datetime] = None) -> List[Fact]:
        idxs = self._by_role.get(role, [])
        result = [self.facts[i] for i in idxs]
        if at is not None:
            result = [f for f in result if f.is_valid_at(at)]
        return result

    def facts_with_value(self, individual: Individual,
                         at: Optional[datetime] = None) -> List[Fact]:
        idxs = self._by_value.get(individual.id, [])
        result = [self.facts[i] for i in idxs]
        if at is not None:
            result = [f for f in result if f.is_valid_at(at)]
        return result

    # --- utilidades --------------------------------------------------------

    def __len__(self) -> int:
        return len(self.facts)

    def summary(self) -> str:
        n_by_axis: Dict[Axis, int] = {}
        for ind in self.individuals.values():
            n_by_axis[ind.axis] = n_by_axis.get(ind.axis, 0) + 1
        parts = [f"Universe '{self.name}'",
                 f"  individuos: {len(self.individuals)}"]
        for ax in Axis:
            if ax in n_by_axis:
                parts.append(f"    {ax.value}: {n_by_axis[ax]}")
        parts.append(f"  hechos:     {len(self.facts)}")
        return "\n".join(parts)
```

---

## §A7 — `ingest.py` — el pipeline de ingesta

96 líneas. Toma un verbo y un diccionario de roles ya identificados (el parser lingüístico se asume externo: lo hace un LLM, o un parser dedicado) y aplica un pipeline de seis pasos para producir una situación reificada (D4) con todos sus hechos atómicos. Es la función que más se usa en los ejemplos de la Parte V del libro.

```python
"""Ingesta: traduce una "oración" (estructurada) a hechos en el universo.

Para el prototipo no parsear español real — eso es trabajo del LLM.
En su lugar exponemos una API de ingesta que recibe verbo + roles ya
identificados y aplica el pipeline:
    1. Resolver lexicon (con polisemia / forma nominal)
    2. Reificar la situación en O
    3. Asentar instancia_de = tipo_situacion
    4. Asentar cada rol como hecho atómico
    5. Validar contra el catálogo D8
    6. Verificar obligatorios

Devuelve la situación reificada para que el caller pueda enriquecerla.
"""

from __future__ import annotations
from datetime import datetime
from typing import Dict, Optional, Any, List

from .axes import Axis
from .individual import Individual, mint_id, category
from .universe import Universe
from .lexicon import Lexicon, LexiconEntry


class IngestError(ValueError):
    pass


def ingest_situation(
    universe: Universe,
    lexicon: Lexicon,
    verb: str,
    roles: Dict[str, Individual],
    *,
    complements: Optional[List[str]] = None,
    nominal: bool = False,
    valid_from: Optional[datetime] = None,
    valid_to: Optional[datetime] = None,
    extra: Optional[Dict[str, Individual]] = None,
    sit_id: Optional[str] = None,
) -> Individual:
    """Ingesta una situación a partir de un verbo y sus roles.

    `roles` mapea NOMBRE_CANÓNICO → Individual (el caller ya resolvió aliases).
    `complements` lista patrones de complemento que disparan polisemia
    (p. ej. ['la_mano'] para `dar la mano`).
    `nominal=True` indica que el "verbo" es en realidad una forma nominal
    ("llegada") y debe buscarse vía `resolve_nominal`.
    `extra` agrega hechos adicionales que no están en la signatura (p. ej.
    `modalidad`, `estatus_factual`, `calificacion`, ...).

    Devuelve la situación reificada en O.
    """
    entry = (
        lexicon.resolve_nominal(verb, complements)
        if nominal else
        lexicon.resolve(verb, complements)
    )
    if entry is None:
        raise IngestError(
            f"Lexicon no tiene entrada para '{verb}' "
            f"con complementos {complements}."
        )

    # Verificar obligatorios
    missing = [r for r in entry.obligatory if r not in roles]
    if missing:
        raise IngestError(
            f"Faltan roles obligatorios para '{verb}': {missing}"
        )

    # Reificar la situación
    sid = sit_id or mint_id(entry.situation_type)
    situ = Individual(id=sid, axis=Axis.O, label=sid)
    universe.add_individual(situ)

    # instancia_de
    tipo = category(entry.situation_type)
    universe.assert_fact(situ, "instancia_de", tipo,
                         valid_from=valid_from, valid_to=valid_to)

    # Roles obligatorios y opcionales
    for role, value in roles.items():
        # No exigimos que esté declarado en la entrada — la entrada es
        # informativa; los extras se admiten. (Política liberal.)
        universe.assert_fact(situ, role, value,
                             valid_from=valid_from, valid_to=valid_to)

    # Extras (modalidad, calificación, ...)
    if extra:
        for role, value in extra.items():
            universe.assert_fact(situ, role, value,
                                 valid_from=valid_from, valid_to=valid_to)

    return situ
```

---

## §A8 — `query.py` — el motor de consulta

124 líneas. Implementa las preguntas-WH como proyecciones sobre hechos. Un `Pattern` declara roles `fixed` (con valores conocidos) y roles `ask` (con `Var` — lo que se quiere descubrir). Soporta filtros por tipo (`type_constraint`) y consultas bitemporales (parámetro `at`). La función `count` es el caso particular de `query` que solo devuelve la cardinalidad.

```python
"""Motor de consulta: las preguntas-WH como proyecciones.

Una consulta es un `Pattern`: un diccionario de roles fijos con valores
conocidos, y al menos un rol marcado como `Var(...)` (la pregunta).
El motor busca todas las situaciones del universo que satisfacen los
roles fijos y proyecta el valor del rol pregunta.

Soporta:
- Consultas puntuales: ¿quién vendió X?
- Consultas temporales: ¿quién era el dueño de X en T0?  (D6)
- Filtros por tipo (instancia_de = K).
- Agregaciones: count, list.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any

from .individual import Individual
from .universe import Universe


@dataclass
class Var:
    """Marcador de variable en un patrón de consulta."""
    name: str = "?"


@dataclass
class Pattern:
    """Patrón de consulta sobre una situación.

    `fixed`: roles cuyo valor está dado (Individual).
    `ask`:   uno o más roles cuyo valor queremos descubrir (Var).
    """
    fixed: Dict[str, Individual] = field(default_factory=dict)
    ask: Dict[str, Var] = field(default_factory=dict)
    type_constraint: Optional[Individual] = None  # filtra por instancia_de = K

    def __post_init__(self):
        # `ask` vacío es válido: cuenta/lista candidatos sin proyección.
        # En ese caso el binding contiene solo `_subject`.
        pass


def query(universe: Universe, pattern: Pattern,
          at: Optional[datetime] = None) -> List[Dict[str, Any]]:
    """Ejecuta el patrón contra el universo. Devuelve una lista de bindings.

    Cada binding es un dict con las claves de `pattern.ask` y los valores
    encontrados (Individual). Las situaciones-candidatas son los sujetos
    que tienen *todos* los roles fijos del patrón (con sus valores) y, si
    aplica, instancia_de = type_constraint.
    """
    # Punto 1: buscar candidatas — sujetos en O que tienen todos los roles
    # del patrón. Tomamos el primer rol fijo (o type_constraint) como ancla
    # para reducir el espacio.

    if pattern.type_constraint is not None:
        # Sujetos cuya instancia_de == type_constraint
        candidate_subjects = {
            f.subject.id
            for f in universe.facts_with_role("instancia_de", at=at)
            if f.value.id == pattern.type_constraint.id
        }
    elif pattern.fixed:
        # Tomamos el primer fixed como ancla.
        role0, val0 = next(iter(pattern.fixed.items()))
        candidate_subjects = {
            f.subject.id
            for f in universe.facts_with_role(role0, at=at)
            if f.value.id == val0.id
        }
    else:
        # Si solo hay ask, buscamos sobre todas las situaciones (raro).
        candidate_subjects = set(universe.individuals.keys())

    # Punto 2: filtrar candidatas por todos los roles fijos
    results: List[Dict[str, Any]] = []
    for sid in candidate_subjects:
        subject = universe.individuals[sid]
        sit_facts = universe.facts_about(subject, at=at)

        # Map role → list of values for this subject
        roles_map: Dict[str, List[Individual]] = {}
        for f in sit_facts:
            roles_map.setdefault(f.role, []).append(f.value)

        # Chequear roles fijos
        ok = True
        for role, expected_val in pattern.fixed.items():
            vals = roles_map.get(role, [])
            if not any(v.id == expected_val.id for v in vals):
                ok = False
                break
        if not ok:
            continue

        # Chequear type_constraint si está
        if pattern.type_constraint is not None:
            instancia_vals = roles_map.get("instancia_de", [])
            if not any(v.id == pattern.type_constraint.id for v in instancia_vals):
                continue

        # Extraer valores para los roles preguntados
        binding: Dict[str, Any] = {"_subject": subject}
        all_present = True
        for ask_role in pattern.ask:
            vals = roles_map.get(ask_role, [])
            if not vals:
                all_present = False
                break
            # Si hay más de uno, devolvemos lista; si uno, el individuo.
            binding[ask_role] = vals[0] if len(vals) == 1 else list(vals)
        if all_present:
            results.append(binding)
    return results


def count(universe: Universe, pattern: Pattern,
          at: Optional[datetime] = None) -> int:
    """Cuenta sujetos que satisfacen el patrón."""
    return len(query(universe, pattern, at=at))
```

---

## §A9 — `__init__.py` — la superficie pública

32 líneas. Lo último que ve quien importa la librería. Reexporta todas las clases y funciones que el usuario va a usar, con un docstring que recapitula qué hace cada pieza. Si alguien escribe `from wq import *`, esto es lo que recibe.

```python
"""WQuestions — prototipo de validación en Python.

Implementa el modelo descrito en `WQuestions.md` y discutido en el libro:
- 8 ejes (Q, O, L, T, N, K, P, M)
- hechos atómicos con signatura tipada
- situaciones reificadas (D4, D5)
- catálogo canónico de roles (D8)
- lexicon con resolución de polisemia (D9)
- vigencia temporal por reificación (D6)
- consultas como proyecciones sobre roles (preguntas-WH)

Se prioriza claridad sobre rendimiento. La meta es validar la arquitectura,
no servir producción.
"""

from .axes import Axis
from .individual import Individual, mint_id, category, quantity, time_point
from .fact import Fact
from .universe import Universe
from .catalog import Catalog, RoleSignature, SignatureError
from .lexicon import Lexicon, LexiconEntry
from .query import Pattern, Var, query, count
from .ingest import ingest_situation, IngestError

__all__ = [
    "Axis", "Individual", "mint_id", "category", "quantity", "time_point",
    "Fact", "Universe",
    "Catalog", "RoleSignature", "SignatureError",
    "Lexicon", "LexiconEntry",
    "Pattern", "Var", "query", "count",
    "ingest_situation", "IngestError",
]
```

---

## Observaciones finales

Si se mira el código completo de la librería en una sola pasada, aparecen seis observaciones que vale la pena nombrar:

1. **Pocas líneas, pocos archivos, pocos conceptos.** Nueve archivos, ~850 líneas, una sola clase principal por archivo. No hay infraestructura inútil, no hay abstracciones especulativas. Cada pieza existe porque el libro la justifica con un capítulo entero.

2. **Las decisiones de diseño se ven en el código.** D3 vive en `fact.py` (la tripleta), D4 vive en `ingest.py` (el reificador), D6 vive en `is_valid_at` (la vigencia), D8 vive en `catalog.py` (las signaturas), D9 vive en `lexicon.py` (los aliases). El paralelismo es directo: una decisión, un módulo.

3. **La política liberal es explícita.** En `catalog.validate`, si el rol no está declarado, *no se valida*. Cuatro líneas de código que materializan la decisión de mantener el modelo extensible sin pelearse con el catálogo central.

4. **La bitemporalidad es ligera.** No hay un sistema bitemporal completo (eso falta para producción — está documentado en el capítulo 26). Lo que hay es un `valid_from`/`valid_to` opcional y un `tx_time` automático: 5 atributos extra sobre `Fact`, una función `is_valid_at` que decide la vigencia, y un parámetro `at=` en todas las consultas. Con eso ya se modelan mudanzas, rediagnósticos, contratos con cláusulas que expiran.

5. **No hay parser de lenguaje natural.** El prototipo asume que el parser es externo — un LLM, o un módulo dedicado que se conecta vía `ingest_situation`. Esto es deliberado: separar la responsabilidad de "entender la oración" (lingüística) de "modelar el hecho" (arquitectura) es lo que permite reutilizar el motor en cualquier idioma y con cualquier parser.

6. **El motor de consulta es ingenuo.** Un barrido sobre el universo con tres índices simples. Sirve para validar el modelo en dominios reales; no sirve para producción a escala. El capítulo 26 enumera los reemplazos productivos: Datalog, SHACL, motores RDF, bases de datos columnar.

Estas seis observaciones, juntas, son la justificación del enfoque del prototipo: **no construir infraestructura; construir prueba de concepto**. Lo que estas 850 líneas demuestran es que el modelo es *coherente* y *operable*. La validación industrial es otro trabajo — el del capítulo 26 y de quien lo continúe.

---

## Lo que queda en el repositorio

Para mantener este anexo manejable solo incluí la librería núcleo. El resto del prototipo — aproximadamente **2.400 líneas adicionales** — está publicado completo en el repositorio del proyecto. Acá va el mapa de lo que vas a encontrar:

```
github.com/joseabantomarin/WQuestions
└── prototipo/
    ├── wq/                       ← incluida en este anexo (850 líneas)
    │   ├── axes.py
    │   ├── individual.py
    │   ├── fact.py
    │   ├── catalog.py
    │   ├── lexicon.py
    │   ├── universe.py
    │   ├── ingest.py
    │   ├── query.py
    │   └── __init__.py
    │
    ├── ejemplos/                 ← no incluida — está en el repo
    │   ├── sauna.py              (532 líneas)
    │   ├── dominios_previos.py   (522 líneas — receta, gol, canción, noticia)
    │   ├── banco.py              (465 líneas)
    │   ├── clinica.py            (312 líneas)
    │   └── taxi.py               (256 líneas)
    │
    └── tests/                    ← no incluida — está en el repo
        └── test_wq.py            (349 líneas)
```

Cada archivo de `ejemplos/` es un script ejecutable que modela un dominio completo: declara los individuos, registra el lexicon, ingresa todas las situaciones, corre las consultas que el libro discute y valida los resultados. Ejecutar uno cualquiera (por ejemplo `python -m prototipo.ejemplos.banco`) reproduce las escenas de la Parte V tal cual aparecen en el libro.

El archivo `test_wq.py` ejercita las invariantes del modelo: que el catálogo valide signaturas, que las consultas bitemporales devuelvan lo correcto en distintos momentos, que la polisemia del lexicon elija la entrada más específica, que la reificación produzca el grafo esperado. Es el cinturón de seguridad que el libro promete cuando dice "todos los tests pasan".

**Cómo correr el prototipo en cinco minutos:**

```bash
git clone https://github.com/joseabantomarin/WQuestions.git
cd WQuestions
python -m prototipo.tests.test_wq          # corre la batería de tests
python -m prototipo.ejemplos.sauna         # ejecuta el dominio del Spa
python -m prototipo.ejemplos.banco         # ejecuta el dominio bancario
```

No hace falta instalar dependencias: el prototipo solo usa la librería estándar de Python. Si lo abres en un editor moderno, los identificadores y las APIs (`Universe`, `ingest_situation`, `Pattern`, `query`) son los mismos que vienen en este anexo, así que la transición entre leer y ejecutar es instantánea.

El prototipo, los ejemplos y los tests son **el espejo operable del libro**. Lo que se afirma en cualquier capítulo de la Parte V se puede ejecutar línea por línea en el repo. Si encuentras una afirmación del libro que no puedas reproducir, el repo tiene un issue tracker abierto — y es exactamente ese tipo de feedback el que el capítulo 26 reclama para que la propuesta deje de ser un texto y se vuelva infraestructura.
