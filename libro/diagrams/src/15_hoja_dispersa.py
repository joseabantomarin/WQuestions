"""Diagrama: el espacio WQuestions como hoja de cálculo dispersa.
Cuatro hechos de dominios distintos viven en la misma estructura tabular.

Salida: ../png/15_hoja_dispersa.png
"""

import os
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

INK = "#1f2937"

# Definición de las filas
ejes = ["Q", "O", "L", "T", "N", "P/M", "K"]
filas = [
    {"hecho": "Receta cocinada",
     "Q": "juan", "O": "preparacion_017", "L": "cocina_casa",
     "T": "2026-05-14T20:00", "N": "—",
     "P/M": "cocinero", "K": "risotto"},
    {"hecho": "Gol marcado",
     "Q": "messi", "O": "gol_001", "L": "estadio_lima",
     "T": "2026-10-14T20:23", "N": "87 (minuto)",
     "P/M": "agente", "K": "gol_jugada_abierta"},
    {"hecho": "Llamada API",
     "Q": "—", "O": "llamada_042", "L": "—",
     "T": "2026-05-14T10:32", "N": "4500 (tokens)",
     "P/M": "tokens_entrada", "K": "llamada_modelo_lenguaje"},
    {"hecho": "Decreto firmado",
     "Q": "ministro_017", "O": "decreto_007", "L": "sede_gobierno",
     "T": "2026-05-14", "N": "50.000.000",
     "P/M": "firmante", "K": "decreto_ejecutivo"},
]

fig, ax = plt.subplots(figsize=(15, 7), dpi=200)
ax.set_xlim(0, 15)
ax.set_ylim(0, 7)
ax.axis("off")
fig.patch.set_facecolor("#ffffff")

# Título
ax.text(7.5, 6.6, "El espacio WQuestions como hoja de cálculo dispersa",
        ha="center", va="center", fontsize=14, fontweight="bold", color=INK)
ax.text(7.5, 6.2,
        "Cuatro filas, cuatro dominios distintos, mismas ocho columnas. Las celdas vacías son la norma, no la excepción.",
        ha="center", va="center", fontsize=10, style="italic", color="#6b7280")

# Geometría de la tabla
HECHO_W = 2.2
COL_W = 1.62
ROW_H = 0.75
TBL_LEFT = 0.4
TBL_TOP = 5.5

# Header de columnas
ax.text(TBL_LEFT + HECHO_W/2, TBL_TOP + 0.3, "Hecho",
        ha="center", va="center", fontsize=11, fontweight="bold", color=INK)
for i, eje in enumerate(ejes):
    x = TBL_LEFT + HECHO_W + i * COL_W + COL_W/2
    # Header con color
    color_eje = {"Q": "#1d4ed8", "O": "#4f46e5", "L": "#059669",
                 "T": "#c2410c", "N": "#b45309", "P/M": "#7c3aed",
                 "K": "#4f46e5"}.get(eje, INK)
    ax.text(x, TBL_TOP + 0.3, eje, ha="center", va="center",
            fontsize=13, fontweight="bold", color=color_eje)

# Línea bajo el header
ax.plot([TBL_LEFT, TBL_LEFT + HECHO_W + len(ejes) * COL_W],
        [TBL_TOP - 0.15, TBL_TOP - 0.15],
        color=INK, linewidth=1.2)

# Filas
for r, fila in enumerate(filas):
    y = TBL_TOP - 0.55 - r * ROW_H
    # Banda alterna
    if r % 2 == 0:
        bg = Rectangle((TBL_LEFT, y - ROW_H/2),
                       HECHO_W + len(ejes) * COL_W, ROW_H,
                       facecolor="#f9fafb", edgecolor="none")
        ax.add_patch(bg)

    # Nombre del hecho
    ax.text(TBL_LEFT + 0.15, y, fila["hecho"],
            ha="left", va="center", fontsize=10, fontweight="bold", color=INK)

    # Celdas
    for i, eje in enumerate(ejes):
        x = TBL_LEFT + HECHO_W + i * COL_W + COL_W/2
        val = fila[eje]
        if val == "—":
            ax.text(x, y, "—", ha="center", va="center",
                    fontsize=11, color="#d1d5db")
        else:
            ax.text(x, y, val, ha="center", va="center",
                    fontsize=8.5, color=INK, family="monospace")

# Línea final
final_y = TBL_TOP - 0.55 - len(filas) * ROW_H + ROW_H/2 - 0.05
ax.plot([TBL_LEFT, TBL_LEFT + HECHO_W + len(ejes) * COL_W],
        [final_y, final_y], color="#9ca3af", linewidth=0.6)

# Anotación: las celdas vacías
empty_x_examples = []
for r, fila in enumerate(filas):
    y = TBL_TOP - 0.55 - r * ROW_H
    for i, eje in enumerate(ejes):
        x = TBL_LEFT + HECHO_W + i * COL_W + COL_W/2
        if fila[eje] == "—":
            circle = plt.Circle((x, y), 0.18, facecolor="none",
                                edgecolor="#ef4444", linewidth=1.2, alpha=0.6)
            ax.add_patch(circle)
            empty_x_examples.append((x, y))

# Pie con anotación
ax.text(7.5, 0.7,
        "Las celdas marcadas con — son dimensiones no aplicables a ese hecho.\n"
        "El espacio es parcial por diseño: ningún hecho ocupa los siete ejes a la vez.",
        ha="center", va="center", fontsize=10, style="italic", color="#6b7280")

# Leyenda visual de cruce de ejes
ax.text(7.5, 0.20,
        "Una consulta filtra por ciertas columnas y devuelve las filas que satisfacen las restricciones.",
        ha="center", va="center", fontsize=9.5, color="#6b7280")

out = os.path.join(os.path.dirname(__file__), "..", "png",
                   "15_hoja_dispersa.png")
plt.savefig(out, dpi=200, bbox_inches="tight", facecolor="#ffffff")
plt.close(fig)
print(f"  ✓ {out}")
