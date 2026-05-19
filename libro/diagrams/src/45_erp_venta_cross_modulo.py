"""Diagrama: la venta cross-módulo del ERP.

Una sola venta genera, simultáneamente, registros en tres módulos
tradicionalmente separados (inventario, contabilidad, RRHH-comisiones).
En sistemas tradicionales esto exige integraciones; en WQuestions es
una situación reificada con tres sub-situaciones ligadas por `parte_de`.

Salida: ../png/45_erp_venta_cross_modulo.png
"""

import os
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

INK = "#1f2937"

# Nodo central — la venta
VENTA_FILL, VENTA_EDGE = "#dbeafe", "#1d4ed8"

# Sub-situaciones — tres módulos
INV_FILL, INV_EDGE = "#dcfce7", "#15803d"      # Inventario — verde
CONT_FILL, CONT_EDGE = "#fef3c7", "#b45309"    # Contabilidad — ámbar
RH_FILL, RH_EDGE = "#fee2e2", "#b91c1c"        # RRHH — rojo

fig, ax = plt.subplots(figsize=(14, 9), dpi=200)
ax.set_xlim(0, 14)
ax.set_ylim(0, 9)
ax.axis("off")
fig.patch.set_facecolor("#ffffff")

# Título
ax.text(7, 8.6,
        "La venta cross-módulo del ERP: un evento, tres módulos, cero ETL",
        ha="center", va="center", fontsize=14, fontweight="bold", color=INK)
ax.text(7, 8.2,
        "Pedro vende 5 bicicletas a BetAuto por 7.500 USD. "
        "Lo que en un ERP tradicional dispara 3 procesos en 3 tablas,",
        ha="center", va="center", fontsize=10, style="italic", color="#6b7280")
ax.text(7, 7.95,
        "en WQuestions es una situación reificada con tres sub-situaciones ligadas por parte_de.",
        ha="center", va="center", fontsize=10, style="italic", color="#6b7280")

# ─────────────────────────────────────────────────────────────
# Nodo central: la venta
# ─────────────────────────────────────────────────────────────
cx, cy = 7.0, 5.6
box_w, box_h = 3.4, 1.4
venta_box = FancyBboxPatch((cx - box_w/2, cy - box_h/2), box_w, box_h,
                           boxstyle="round,pad=0.06",
                           facecolor=VENTA_FILL, edgecolor=VENTA_EDGE,
                           linewidth=2.4)
ax.add_patch(venta_box)
ax.text(cx, cy + 0.35, "venta_001",
        ha="center", va="center", fontsize=12, fontweight="bold",
        color=VENTA_EDGE, family="monospace")
ax.text(cx, cy + 0.08, "instancia_de: accion_vender",
        ha="center", va="center", fontsize=8.5, color="#374151",
        family="monospace")
ax.text(cx, cy - 0.12,
        "agente: Pedro  ·  cliente: BetAuto",
        ha="center", va="center", fontsize=8, color="#374151")
ax.text(cx, cy - 0.32,
        "tema: bicicleta  ·  monto: 7.500 USD",
        ha="center", va="center", fontsize=8, color="#374151")
ax.text(cx, cy - 0.52,
        "momento: 2026-07-15 11:20",
        ha="center", va="center", fontsize=8, color="#6b7280", style="italic")

# ─────────────────────────────────────────────────────────────
# Tres sub-situaciones colgando por parte_de
# ─────────────────────────────────────────────────────────────
def sub_box(x, y, title, color_fill, color_edge, lines):
    sub_w, sub_h = 3.5, 1.7
    box = FancyBboxPatch((x - sub_w/2, y - sub_h/2), sub_w, sub_h,
                         boxstyle="round,pad=0.05",
                         facecolor=color_fill, edgecolor=color_edge,
                         linewidth=1.6)
    ax.add_patch(box)
    ax.text(x, y + sub_h/2 - 0.25, title,
            ha="center", va="center", fontsize=10.5, fontweight="bold",
            color=color_edge, family="monospace")
    for i, line in enumerate(lines):
        ax.text(x, y + 0.18 - i * 0.22, line,
                ha="center", va="center", fontsize=8,
                color="#374151")
    return (x, y + sub_h/2)

# Sub 1 — inventario (izquierda)
top_inv = sub_box(2.4, 2.6, "mov_inventario_001",
                  INV_FILL, INV_EDGE,
                  ["MÓDULO INVENTARIO",
                   "tipo: salida del almacén",
                   "cantidad: 5 unidades",
                   "origen: almacen_central"])

# Sub 2 — asiento contable (centro)
top_cont = sub_box(7.0, 2.6, "asiento_venta_001",
                   CONT_FILL, CONT_EDGE,
                   ["MÓDULO CONTABILIDAD",
                    "tipo: ingreso por venta",
                    "monto: 7.500 USD",
                    "moneda: USD"])

# Sub 3 — comisión (derecha)
top_rh = sub_box(11.6, 2.6, "comision_pedro_001",
                 RH_FILL, RH_EDGE,
                 ["MÓDULO RRHH",
                  "tipo: comisión vendedor",
                  "beneficiario: Pedro",
                  "monto: 375 USD (5%)"])

# ─────────────────────────────────────────────────────────────
# Flechas con etiqueta "parte_de"
# ─────────────────────────────────────────────────────────────
def parte_de_arrow(src_x, src_y, dest_x, dest_y, color):
    arr = FancyArrowPatch((dest_x, dest_y), (src_x, src_y),
                          arrowstyle="-|>", mutation_scale=14,
                          color=color, linewidth=1.5,
                          connectionstyle="arc3,rad=0.0")
    ax.add_patch(arr)
    # Etiqueta parte_de en el medio
    mx, my = (src_x + dest_x) / 2, (src_y + dest_y) / 2
    ax.text(mx, my + 0.10, "parte_de",
            ha="center", va="center", fontsize=8.5,
            color=color, fontweight="bold", family="monospace",
            bbox=dict(boxstyle="round,pad=0.18",
                      facecolor="white", edgecolor="none", alpha=0.9))

parte_de_arrow(cx - 0.8, cy - box_h/2, top_inv[0], top_inv[1], INV_EDGE)
parte_de_arrow(cx,       cy - box_h/2, top_cont[0], top_cont[1], CONT_EDGE)
parte_de_arrow(cx + 0.8, cy - box_h/2, top_rh[0], top_rh[1], RH_EDGE)

# ─────────────────────────────────────────────────────────────
# Pie explicativo
# ─────────────────────────────────────────────────────────────
ax.text(7, 0.85,
        "En un ERP tradicional: 3 tablas, 3 procesos, foreign keys, ETL para reportes cross-módulo.",
        ha="center", va="center", fontsize=10, color="#9ca3af",
        style="italic")
ax.text(7, 0.45,
        "En WQuestions: 3 sub-situaciones, una sola consulta `parte_de` para reconstruir todo el efecto de la venta.",
        ha="center", va="center", fontsize=10.5, color="#15803d",
        fontweight="bold")

out = os.path.join(os.path.dirname(__file__), "..", "png",
                   "45_erp_venta_cross_modulo.png")
plt.savefig(out, dpi=200, bbox_inches="tight", facecolor="#ffffff")
plt.close(fig)
print(f"  ✓ {out}")
