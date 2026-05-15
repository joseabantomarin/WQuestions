"""Diagrama: mapa del dominio sauna sobre los seis ejes de valor.
Cada eje es una banda horizontal con las entidades concretas del dominio.

Salida: ../png/27_mapa_sauna.png
"""

import os
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

INK = "#1f2937"

# Paleta por eje (consistente con diagramas previos)
AXES = [
    {"code": "Q", "name": "quién",  "fill": "#dbeafe", "edge": "#1d4ed8",
        "items": ["Ana", "Beto", "Carlos", "Anita (recep.)", "Sauna Oasis"]},
    {"code": "O", "name": "qué",    "fill": "#dcfce7", "edge": "#15803d",
        "items": ["sesion_ana_07", "pago_001", "plan_carlos_001",
                  "promo_masaje", "reco_ducha_fría", "residencia_001"]},
    {"code": "L", "name": "dónde",  "fill": "#fef3c7", "edge": "#b45309",
        "items": ["sauna_oasis_central", "cámara_vapor_1",
                  "cámara_vapor_2", "cámara_seca", "ducha_03"]},
    {"code": "T", "name": "cuándo", "fill": "#fed7aa", "edge": "#c2410c",
        "items": ["2026-04-22 18:00", "semana_2026_w17",
                  "mes_2026_04", "inicio_plan: 2026-04-01"]},
    {"code": "N", "name": "cuánto", "fill": "#e9d5ff", "edge": "#7c3aed",
        "items": ["20 USD (sesión)", "60 °C (cámara)",
                  "20 min (recomendación)", "7 (visitas → 1 gratis)",
                  "2 sesiones/semana (plan)"]},
    {"code": "K", "name": "clase",  "fill": "#e0e7ff", "edge": "#4f46e5",
        "items": ["servicio_sauna", "finalizada", "real", "intencionado",
                  "volitiva", "Currency:USD", "Temperature:Cel"]},
]

fig, ax = plt.subplots(figsize=(15, 9.5), dpi=200)
ax.set_xlim(0, 15)
ax.set_ylim(0, 9.5)
ax.axis("off")
fig.patch.set_facecolor("#ffffff")

# Título
ax.text(7.5, 9.10, "El dominio sauna mapeado a los 6 ejes de valor",
        ha="center", va="center", fontsize=14, fontweight="bold", color=INK)
ax.text(7.5, 8.70,
        "Cada eje aloja entidades de naturaleza homogénea. Los predicados P/M conectan unas con otras.",
        ha="center", va="center", fontsize=10, style="italic", color="#6b7280")

# Bandas (de arriba hacia abajo)
band_height = 1.05
gap = 0.10
total = len(AXES) * (band_height + gap) - gap
start_y = 7.95 - 0.30  # arriba de la primera banda
for i, ax_info in enumerate(AXES):
    by = start_y - i * (band_height + gap)
    # Caja de la banda
    box = FancyBboxPatch((0.6, by - band_height), 13.8, band_height,
                         boxstyle="round,pad=0.04",
                         facecolor=ax_info["fill"], edgecolor=ax_info["edge"],
                         linewidth=1.6)
    ax.add_patch(box)
    # Etiqueta del eje (izquierda)
    code = ax_info["code"]
    chip = FancyBboxPatch((0.8, by - band_height + 0.18), 0.55, 0.55,
                          boxstyle="round,pad=0.02",
                          facecolor=ax_info["edge"], edgecolor="none")
    ax.add_patch(chip)
    ax.text(1.075, by - band_height + 0.455, code,
            ha="center", va="center", fontsize=13,
            color="white", fontweight="bold", family="monospace")
    ax.text(1.5, by - band_height + 0.78, ax_info["name"],
            ha="left", va="center", fontsize=10.5, fontweight="bold",
            color=ax_info["edge"])
    ax.text(1.5, by - band_height + 0.30,
            f"({len(ax_info['items'])} ejemplos)",
            ha="left", va="center", fontsize=8.5,
            style="italic", color=ax_info["edge"])

    # Items (centro y derecha)
    items = ax_info["items"]
    n_items = len(items)
    item_x_start = 3.2
    item_x_end = 14.2
    col_w = (item_x_end - item_x_start) / max(n_items, 1)
    for j, item in enumerate(items):
        ix = item_x_start + (j + 0.5) * col_w
        ax.text(ix, by - band_height/2, item,
                ha="center", va="center", fontsize=8.5,
                color=ax_info["edge"], family="monospace",
                bbox=dict(boxstyle="round,pad=0.18", facecolor="white",
                          edgecolor=ax_info["edge"], linewidth=0.8, alpha=0.95))

# Pie
ax.text(7.5, 0.30,
        "Un dominio comercial pequeño cruza los 6 ejes de valor sin esfuerzo. Los predicados (P, M) son el cableado.",
        ha="center", va="center", fontsize=9.5, style="italic", color="#6b7280")

out = os.path.join(os.path.dirname(__file__), "..", "png",
                   "27_mapa_sauna.png")
plt.savefig(out, dpi=200, bbox_inches="tight", facecolor="#ffffff")
plt.close(fig)
print(f"  ✓ {out}")
