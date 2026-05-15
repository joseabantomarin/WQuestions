"""Diagrama: el verbo como signatura tipada.
Tres verbos del español mostrados como declaraciones de función, con sus
roles obligatorios y opcionales, y el eje al que apunta cada uno.

Salida: ../png/21_verbo_signatura.png
"""

import os
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

INK = "#1f2937"
TYPE_COLORS = {
    "Q": "#1d4ed8",
    "O": "#15803d",
    "L": "#b45309",
    "T": "#c2410c",
    "N": "#7c3aed",
    "K": "#4f46e5",
}

fig, ax = plt.subplots(figsize=(14, 9), dpi=200)
ax.set_xlim(0, 14)
ax.set_ylim(0, 9)
ax.axis("off")
fig.patch.set_facecolor("#ffffff")

# Título
ax.text(7, 8.55, "El verbo como signatura tipada",
        ha="center", va="center", fontsize=14, fontweight="bold", color=INK)
ax.text(7, 8.15,
        "Cada verbo declara qué roles acepta, cuáles son obligatorios y de qué eje viene cada uno.",
        ha="center", va="center", fontsize=10, style="italic", color="#6b7280")

verbs = [
    {
        "name": "dar",
        "y": 6.6,
        "params": [
            ("agente",          "Q", True),
            ("tema",            "O", True),
            ("beneficiario",    "Q", True),
            ("momento",         "T", False),
            ("lugar_de",        "L", False),
            ("con_finalidad",   "O", False),
        ],
    },
    {
        "name": "vender",
        "y": 4.3,
        "params": [
            ("agente",          "Q", True),
            ("tema",            "O", True),
            ("comprador",       "Q", True),
            ("monto",           "N", True),
            ("unidad",          "K", True),
            ("momento",         "T", False),
        ],
    },
    {
        "name": "ingresar",
        "y": 2.0,
        "params": [
            ("agente",          "Q", True),
            ("lugar_destino",   "L", True),
            ("momento",         "T", False),
            ("con_finalidad",   "O", False),
        ],
    },
]

# Layout: verbo grande a la izquierda; bajo el verbo, los parámetros
# en columnas centradas a partir de un base_x consistente.
box_x = 0.8
box_w = 12.4
inner_h = 1.85

for v in verbs:
    y = v["y"]
    name = v["name"]
    params = v["params"]

    # Caja contenedora
    box = FancyBboxPatch((box_x, y - 0.95), box_w, inner_h,
                         boxstyle="round,pad=0.05",
                         facecolor="#f9fafb", edgecolor="#9ca3af", linewidth=1.0)
    ax.add_patch(box)

    # Nombre del verbo (grande, izquierda)
    ax.text(box_x + 0.4, y + 0.55, name,
            ha="left", va="center", fontsize=15, fontweight="bold",
            color=INK, family="monospace")
    ax.text(box_x + 0.4, y - 0.55, "→ situación",
            ha="left", va="center", fontsize=9.5, style="italic",
            color="#15803d", family="monospace")

    # Parámetros en grid: 6 columnas máximo, alineadas
    n_cols = 6
    grid_left = box_x + 2.8
    grid_right = box_x + box_w - 0.4
    col_w = (grid_right - grid_left) / n_cols
    for i, (pname, ptype, mand) in enumerate(params):
        col_cx = grid_left + (i + 0.5) * col_w
        color = TYPE_COLORS[ptype]
        suffix = "" if mand else "?"
        # nombre del parámetro
        ax.text(col_cx, y + 0.50, f"{pname}{suffix}",
                ha="center", va="center", fontsize=9.5,
                color="#374151", family="monospace",
                fontweight="bold" if mand else "normal")
        # chip del tipo
        chip = FancyBboxPatch((col_cx - 0.22, y + 0.05), 0.44, 0.34,
                              boxstyle="round,pad=0.02",
                              facecolor=color, edgecolor="none")
        ax.add_patch(chip)
        ax.text(col_cx, y + 0.22, ptype,
                ha="center", va="center", fontsize=10.5,
                color="white", fontweight="bold", family="monospace")
        # estado (obligatorio / opcional)
        status = "obligatorio" if mand else "opcional"
        ax.text(col_cx, y - 0.35, status,
                ha="center", va="center", fontsize=7.5,
                style="italic", color="#6b7280")

# Leyenda inferior (espacio limpio)
leg_y = 0.6
ax.text(0.8, leg_y, "Tipos:", ha="left", va="center",
        fontsize=10, fontweight="bold", color="#374151")
items = [("Q", "agentes"), ("O", "objetos/situaciones"), ("L", "lugares"),
         ("T", "tiempos"), ("N", "magnitudes"), ("K", "categorías")]
xpos = 1.85
for code, name in items:
    chip = FancyBboxPatch((xpos, leg_y - 0.18), 0.35, 0.36,
                          boxstyle="round,pad=0.02",
                          facecolor=TYPE_COLORS[code], edgecolor="none")
    ax.add_patch(chip)
    ax.text(xpos + 0.175, leg_y, code,
            ha="center", va="center", fontsize=10,
            color="white", fontweight="bold", family="monospace")
    ax.text(xpos + 0.45, leg_y, name,
            ha="left", va="center", fontsize=9.5, color="#6b7280")
    xpos += 1.85

out = os.path.join(os.path.dirname(__file__), "..", "png",
                   "21_verbo_signatura.png")
plt.savefig(out, dpi=200, bbox_inches="tight", facecolor="#ffffff")
plt.close(fig)
print(f"  ✓ {out}")
