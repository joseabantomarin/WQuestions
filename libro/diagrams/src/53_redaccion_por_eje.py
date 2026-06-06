"""Diagrama 53: redacción por eje.

La misma situación, mostrada a dos solicitantes distintos. Unos ejes se
revelan (qué, cuándo); otros quedan bajo candado (cuánto, quién). La
divulgación diferencial vive en la geometría del hecho.

Salida: ../png/53_redaccion_por_eje.png
"""

import os
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

INK = "#1f2937"
AZUL_BG, AZUL_BD = "#e0e7ff", "#4f46e5"
VERDE_BD = "#15803d"
ROJO = "#b91c1c"
GRIS_BG, GRIS_BD = "#e5e7eb", "#9ca3af"

fig, ax = plt.subplots(figsize=(14, 8.5), dpi=200)
ax.set_xlim(0, 14)
ax.set_ylim(0, 8.5)
ax.axis("off")
fig.patch.set_facecolor("#ffffff")

ax.text(7.0, 8.10, "La misma situación, dos divulgaciones distintas",
        ha="center", va="center", fontsize=14, fontweight="bold", color=INK)
ax.text(7.0, 7.65, "situación: «transacción_2026_8841»",
        ha="center", va="center", fontsize=10, style="italic", color=GRIS_BD)

# los cuatro ejes de la situación
ejes = ["qué (O): transferencia", "cuándo (T): 2026-04-09",
        "cuánto (N): S/ 42 000", "quién (Q): contraparte Pérez"]

# dos columnas: auditor financiero vs investigador
columnas = [
    (3.6, "Auditor financiero", [True, True, False, False]),
    (10.4, "Investigador epidemiológico", [False, True, False, False]),
]

for col_x, titulo, visibles in columnas:
    ax.add_patch(FancyBboxPatch((col_x - 2.7, 6.1), 5.4, 0.7,
                                boxstyle="round,pad=0.05",
                                facecolor="#f3f4f6", edgecolor=INK, linewidth=1.2))
    ax.text(col_x, 6.45, titulo, ha="center", va="center",
            fontsize=11, fontweight="bold", color=INK)

    for j, (eje, vis) in enumerate(zip(ejes, visibles)):
        ey = 5.3 - j * 1.05
        if vis:
            bg, bd, fg = AZUL_BG, AZUL_BD, INK
            etiqueta = eje
            marca, marca_col = "✓ visible", VERDE_BD
        else:
            bg, bd, fg = GRIS_BG, GRIS_BD, GRIS_BD
            etiqueta = eje.split(":")[0] + ": —— sellado ——"
            marca, marca_col = "● oculto", ROJO
        ax.add_patch(FancyBboxPatch((col_x - 2.7, ey - 0.4), 5.4, 0.8,
                                    boxstyle="round,pad=0.04",
                                    facecolor=bg, edgecolor=bd, linewidth=1.3))
        ax.text(col_x - 2.5, ey, etiqueta, ha="left", va="center",
                fontsize=9.5, color=fg)
        ax.text(col_x + 2.5, ey, marca, ha="right", va="center",
                fontsize=8.5, fontweight="bold", color=marca_col)

ax.text(7.0, 0.55,
        "El auditor sabe que la transacción ocurrió, sin ver el monto ni la contraparte.\n"
        "El investigador solo recibe la fecha. La minimización es estructural, no una promesa.",
        ha="center", va="center", fontsize=9.5, color="#374151")

out = os.path.join(os.path.dirname(__file__), "..", "png", "53_redaccion_por_eje.png")
plt.savefig(out, dpi=200, bbox_inches="tight", facecolor="#ffffff")
plt.close(fig)
print(f"  ✓ {out}")
