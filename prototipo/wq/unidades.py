"""El subconjunto de QUDT que el prototipo trae de fábrica.

El capítulo 4 fija la regla: si la unidad existe en QUDT, se usa QUDT, y una
unidad que WQuestions adopta se enlaza al catálogo público en vez de
inventarse. Esto siembra las unidades corrientes con su ancla, su dimensión y
su factor exacto, todo como tripletas colgando de K.

Lo que se siembra aquí no agota nada. Un dominio declara las suyas con
`declarar_unidad`, y las que ningún catálogo cataloga todavía (el token de un
modelo de lenguaje, el dólar por millón de tokens) se declaran igual, sin ancla.
"""

from __future__ import annotations

from .derivacion import declarar_unidad, declarar_unidades_base

QUDT = "http://qudt.org/vocab/unit/"


def sembrar_si(universe) -> None:
    """Unidades base y derivadas de uso corriente, con factores exactos."""
    declarar_unidades_base(universe)

    # -- bases -------------------------------------------------------------
    declarar_unidad(universe, "K:Gramo", label="gramo", qudt=QUDT + "GM")
    declarar_unidad(universe, "K:Metro", label="metro", qudt=QUDT + "M")
    declarar_unidad(universe, "K:Segundo", label="segundo", qudt=QUDT + "SEC")
    declarar_unidad(universe, "K:Litro", label="litro", qudt=QUDT + "L")

    # -- masa --------------------------------------------------------------
    declarar_unidad(universe, "K:Miligramo", label="miligramo",
                    base="K:Gramo", factor=1e-3, qudt=QUDT + "MilliGM")
    declarar_unidad(universe, "K:Kilogramo", label="kilogramo",
                    base="K:Gramo", factor=1e3, qudt=QUDT + "KiloGM")
    declarar_unidad(universe, "K:ToneladaMetrica", label="tonelada métrica",
                    base="K:Gramo", factor=1e6, qudt=QUDT + "TONNE")
    # La onza troy: 31,1034768 g exactos. Redondearla a 31,1 es de dónde salen
    # los descuadres de una décima en los reportes de metal precioso.
    declarar_unidad(universe, "K:OnzaTroy", label="onza troy",
                    base="K:Gramo", factor=31.1034768, qudt=QUDT + "OZ_TROY")

    # -- longitud ----------------------------------------------------------
    declarar_unidad(universe, "K:Milimetro", label="milímetro",
                    base="K:Metro", factor=1e-3, qudt=QUDT + "MilliM")

    # -- tiempo ------------------------------------------------------------
    declarar_unidad(universe, "K:Minuto", label="minuto",
                    base="K:Segundo", factor=60, qudt=QUDT + "MIN")
    declarar_unidad(universe, "K:Hora", label="hora",
                    base="K:Segundo", factor=3600, qudt=QUDT + "HR")
    declarar_unidad(universe, "K:Anio", label="año",
                    base="K:Segundo", factor=31_557_600, qudt=QUDT + "YR")

    # -- adimensionales con escala ----------------------------------------
    declarar_unidad(universe, "K:Porcentaje", label="porcentaje",
                    factor=0.01, qudt=QUDT + "PERCENT")

    # -- compuestas: razones entre magnitudes que el eje ya sabe nombrar ---
    declarar_unidad(universe, "K:GramoPorTonelada", label="gramo por tonelada",
                    numerador="K:Gramo", denominador="K:ToneladaMetrica")
    declarar_unidad(universe, "K:MiligramoPorLitro", label="miligramo por litro",
                    numerador="K:Miligramo", denominador="K:Litro")
    declarar_unidad(universe, "K:ToneladaPorHora", label="tonelada por hora",
                    numerador="K:ToneladaMetrica", denominador="K:Hora")
    declarar_unidad(universe, "K:MilimetroPorSegundo",
                    label="milímetro por segundo",
                    numerador="K:Milimetro", denominador="K:Segundo")
