"""Diagrama: mapa del dominio bancario sobre los seis ejes de valor.

Cada eje es una banda horizontal con las entidades concretas del dominio.

Salida: ../png/41_mapa_banco.png
"""

import os
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

INK = "#1f2937"

AXES = [
    {"code": "Q", "name": "quién",  "fill": "#dbeafe", "edge": "#1d4ed8",
        "items": ["Cliente retail", "Empresa corp.", "Empleado",
                  "Banco S.A.", "Motor antifraude", "Visa/MC"]},
    {"code": "O", "name": "qué",    "fill": "#dcfce7", "edge": "#15803d",
        "items": ["cuenta_ahorros", "préstamo_personal", "tarjeta_visa",
                  "transferencia", "asiento_contable", "oferta_visa_pt",
                  "investig_fraude"]},
    {"code": "L", "name": "dónde",  "fill": "#fef3c7", "edge": "#b45309",
        "items": ["casa matriz", "sucursal_centro", "ATM_001",
                  "web banking", "mobile app", "POS comercial"]},
    {"code": "T", "name": "cuándo", "fill": "#fed7aa", "edge": "#c2410c",
        "items": ["t. operativo", "t. contable", "fecha cierre",
                  "vencimiento cuota"]},
    {"code": "N", "name": "cuánto", "fill": "#e9d5ff", "edge": "#7c3aed",
        "items": ["500 USD", "5000 USD (capital)", "18% (tasa)",
                  "36 cuotas", "850 (score)"]},
    {"code": "K", "name": "clase",  "fill": "#e0e7ff", "edge": "#4f46e5",
        "items": ["Currency:USD", "Currency:PEN", "vigente", "mora_60",
                  "castigado", "Platinum", "KYC_completo"]},
]

fig, ax = plt.subplots(figsize=(16, 9.5), dpi=200)
ax.set_xlim(0, 16)
ax.set_ylim(0, 9.5)
ax.axis("off")
fig.patch.set_facecolor("#ffffff")

ax.text(8, 9.10, "El dominio bancario sobre los 6 ejes de valor",
        ha="center", va="center", fontsize=14, fontweight="bold", color=INK)
ax.text(8, 8.70,
        "Tres clases de Q, seis familias de O, multi-canal en L, T triple, N+K obligatorio en todo importe.",
        ha="center", va="center", fontsize=10, style="italic", color="#6b7280")

band_height = 1.05
gap = 0.10
start_y = 7.95
for i, ax_info in enumerate(AXES):
    by = start_y - i * (band_height + gap)
    box = FancyBboxPatch((0.6, by - band_height), 14.8, band_height,
                         boxstyle="round,pad=0.04",
                         facecolor=ax_info["fill"], edgecolor=ax_info["edge"],
                         linewidth=1.6)
    ax.add_patch(box)
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

    items = ax_info["items"]
    n_items = len(items)
    item_x_start = 3.2
    item_x_end = 15.2
    col_w = (item_x_end - item_x_start) / max(n_items, 1)
    for j, item in enumerate(items):
        ix = item_x_start + (j + 0.5) * col_w
        ax.text(ix, by - band_height/2, item,
                ha="center", va="center", fontsize=8.5,
                color=ax_info["edge"], family="monospace",
                bbox=dict(boxstyle="round,pad=0.18", facecolor="white",
                          edgecolor=ax_info["edge"], linewidth=0.8, alpha=0.95))

ax.text(8, 0.30,
        "Industrial: miles de Q, millones de O, cinco a diez canales L, T triplemente registrado, todo importe con N+K.",
        ha="center", va="center", fontsize=9.5, style="italic", color="#6b7280")

out = os.path.join(os.path.dirname(__file__), "..", "png",
                   "41_mapa_banco.png")
plt.savefig(out, dpi=200, bbox_inches="tight", facecolor="#ffffff")
plt.close(fig)
print(f"  ✓ {out}")
