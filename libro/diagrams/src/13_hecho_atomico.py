"""Diagrama: el hecho atómico — sujeto, predicado, objeto con signatura tipada.
Muestra cómo cada hecho lleva implícita la signatura de qué eje a qué eje.

Salida: ../png/13_hecho_atomico.png
"""

import os
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

INK = "#1f2937"

# Diferentes hechos como ejemplos
hechos = [
    {"suj": "paciente_042", "suj_eje": "Q", "pred": "edad", "obj": "42", "obj_eje": "N",
     "color_suj": "#dbeafe", "color_obj": "#fef3c7",
     "edge_suj": "#1d4ed8", "edge_obj": "#b45309", "tipo_pred": "P"},
    {"suj": "gol_001", "suj_eje": "O", "pred": "agente", "obj": "messi", "obj_eje": "Q",
     "color_suj": "#e0e7ff", "color_obj": "#dbeafe",
     "edge_suj": "#4f46e5", "edge_obj": "#1d4ed8", "tipo_pred": "M"},
    {"suj": "cancion_yesterday", "suj_eje": "O", "pred": "compositor", "obj": "mccartney", "obj_eje": "Q",
     "color_suj": "#e0e7ff", "color_obj": "#dbeafe",
     "edge_suj": "#4f46e5", "edge_obj": "#1d4ed8", "tipo_pred": "P"},
    {"suj": "decreto_017", "suj_eje": "O", "pred": "fecha_publicacion", "obj": "2026-05-14", "obj_eje": "T",
     "color_suj": "#e0e7ff", "color_obj": "#dcfce7",
     "edge_suj": "#4f46e5", "edge_obj": "#15803d", "tipo_pred": "P"},
    {"suj": "llamada_api_042", "suj_eje": "O", "pred": "tokens_entrada", "obj": "4500", "obj_eje": "N",
     "color_suj": "#e0e7ff", "color_obj": "#fef3c7",
     "edge_suj": "#4f46e5", "edge_obj": "#b45309", "tipo_pred": "P"},
]

fig, ax = plt.subplots(figsize=(13, 8), dpi=200)
ax.set_xlim(0, 13)
ax.set_ylim(0, 8)
ax.axis("off")
fig.patch.set_facecolor("#ffffff")

# Título
ax.text(6.5, 7.6, "El hecho atómico: sujeto · predicado · objeto",
        ha="center", va="center", fontsize=14, fontweight="bold", color=INK)
ax.text(6.5, 7.2,
        "Misma forma para todo dominio. Lo que distingue cada hecho es la signatura tipada del predicado.",
        ha="center", va="center", fontsize=10, style="italic", color="#6b7280")

# Una tabla visual: cada hecho como una fila
PRED_COLOR = {"P": "#1d4ed8", "M": "#b45309"}

y = 6.0
for h in hechos:
    # Sujeto
    suj_box = FancyBboxPatch((0.4, y - 0.4), 2.6, 0.8,
                             boxstyle="round,pad=0.04",
                             facecolor=h["color_suj"], edgecolor=h["edge_suj"], linewidth=1.4)
    ax.add_patch(suj_box)
    ax.text(1.7, y + 0.05, h["suj"], ha="center", va="center",
            fontsize=10, fontweight="bold", color=h["edge_suj"], family="monospace")
    ax.text(1.7, y - 0.20, f"∈ {h['suj_eje']}", ha="center", va="center",
            fontsize=8, style="italic", color="#6b7280")

    # Flecha-predicado con etiqueta P/M
    arrow = FancyArrowPatch((3.0, y), (8.6, y), arrowstyle="-|>",
                            mutation_scale=14,
                            color=PRED_COLOR[h["tipo_pred"]], linewidth=1.6)
    ax.add_patch(arrow)
    ax.text(5.8, y + 0.20, h["pred"], ha="center", va="center",
            fontsize=10, style="italic", color=PRED_COLOR[h["tipo_pred"]],
            bbox=dict(boxstyle="round,pad=0.15", facecolor="white",
                      edgecolor=PRED_COLOR[h["tipo_pred"]], linewidth=0.8, alpha=0.95))
    ax.text(5.8, y - 0.30, f"∈ {h['tipo_pred']}",
            ha="center", va="center", fontsize=7.5, style="italic",
            color=PRED_COLOR[h["tipo_pred"]])

    # Objeto
    obj_box = FancyBboxPatch((8.7, y - 0.4), 3.9, 0.8,
                             boxstyle="round,pad=0.04",
                             facecolor=h["color_obj"], edgecolor=h["edge_obj"], linewidth=1.4)
    ax.add_patch(obj_box)
    ax.text(10.65, y + 0.05, h["obj"], ha="center", va="center",
            fontsize=10, fontweight="bold", color=h["edge_obj"], family="monospace")
    ax.text(10.65, y - 0.20, f"∈ {h['obj_eje']}", ha="center", va="center",
            fontsize=8, style="italic", color="#6b7280")

    y -= 1.05

# Pie
ax.text(6.5, 0.55,
        "Cada hecho atómico es independiente, tipado y componible.",
        ha="center", va="center", fontsize=10, fontweight="bold", color=INK)
ax.text(6.5, 0.25,
        "Las cosas complejas se describen acumulando hechos sobre sujetos compartidos.",
        ha="center", va="center", fontsize=9.5, style="italic", color="#6b7280")

out = os.path.join(os.path.dirname(__file__), "..", "png",
                   "13_hecho_atomico.png")
plt.savefig(out, dpi=200, bbox_inches="tight", facecolor="#ffffff")
plt.close(fig)
print(f"  ✓ {out}")
