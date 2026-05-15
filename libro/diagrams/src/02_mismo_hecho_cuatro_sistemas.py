"""Diagrama: el mismo hecho ('persona compra producto') registrado en 4 sistemas
con vocabularios incompatibles. Refuerza la 'torre de Babel' del capítulo 1.

Salida: ../png/02_mismo_hecho_cuatro_sistemas.png
"""

import os
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

INK = "#1f2937"
SYS_COLORS = {
    "pos":       ("#dbeafe", "#1d4ed8"),  # azul
    "contable":  ("#fce7f3", "#9f1239"),  # rosa
    "marketing": ("#dcfce7", "#15803d"),  # verde
    "inventario":("#fef3c7", "#b45309"),  # ámbar
}

systems = [
    ("pos",       "Punto de venta",   "ventas(id, cliente_id,\n  producto_id, monto,\n  fecha, vendedor_id)"),
    ("contable",  "Sistema contable", "asiento:\n  debe: ctas_x_cobrar 49.90\n  haber: ventas_brutas 42.29\n  haber: impuesto 7.61"),
    ("marketing", "Marketing",        "event: purchase_completed\nuser_id: u_1042\nproduct_sku: sku-88\nrevenue: 49.90\nchannel: store"),
    ("inventario","Inventario",       "movimiento: salida\nproducto: 88\ncantidad: 1\nalmacen: tienda_central"),
]

fig, ax = plt.subplots(figsize=(11, 7), dpi=200)
ax.set_xlim(0, 11)
ax.set_ylim(0, 7)
ax.axis("off")
fig.patch.set_facecolor("#ffffff")

# Hecho central
hecho_box = FancyBboxPatch((4, 5.6), 3, 1, boxstyle="round,pad=0.08",
                           facecolor="#f9fafb", edgecolor=INK, linewidth=2)
ax.add_patch(hecho_box)
ax.text(5.5, 6.35, "El mismo hecho", ha="center", va="center",
        fontsize=12, fontweight="bold", color=INK)
ax.text(5.5, 5.95, "una persona compra un\nproducto en una tienda",
        ha="center", va="center", fontsize=10, style="italic", color=INK)

# Cuatro sistemas en torno
positions = [(0.4, 3.0), (3.0, 0.4), (6.0, 0.4), (8.6, 3.0)]
for (key, name, body), (x, y) in zip(systems, positions):
    fill, edge = SYS_COLORS[key]
    box = FancyBboxPatch((x, y), 2.4, 1.9, boxstyle="round,pad=0.05",
                         facecolor=fill, edgecolor=edge, linewidth=1.5)
    ax.add_patch(box)
    ax.text(x + 1.2, y + 1.65, name, ha="center", va="center",
            fontsize=11, fontweight="bold", color=edge)
    ax.text(x + 1.2, y + 0.75, body, ha="center", va="center",
            fontsize=8, family="monospace", color=INK)
    # Flecha desde el hecho central al sistema
    arrow = FancyArrowPatch((5.5, 5.6), (x + 1.2, y + 1.9),
                            arrowstyle="-|>", mutation_scale=12,
                            color="#9ca3af", linewidth=1, linestyle="--",
                            connectionstyle="arc3,rad=0.0")
    ax.add_patch(arrow)

# Título
ax.text(5.5, 6.85, "Torre de Babel: el mismo hecho en cuatro idiomas",
        ha="center", va="center", fontsize=14, fontweight="bold", color=INK)

# Pie
ax.text(5.5, 0.05,
        "cuatro vocabularios incompatibles describiendo el mismo evento del mundo",
        ha="center", va="center", fontsize=9, style="italic", color="#6b7280")

out = os.path.join(os.path.dirname(__file__), "..", "png",
                   "02_mismo_hecho_cuatro_sistemas.png")
plt.savefig(out, dpi=200, bbox_inches="tight", facecolor="#ffffff")
plt.close(fig)
print(f"  ✓ {out}")
