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
