"""Diagrama: la cadena normativa de un acto municipal.

Muestra cómo una multa de tránsito está conectada hacia atrás con
dos cadenas distintas: la cadena causal (la infracción que la provocó)
y la cadena normativa (el artículo de la ordenanza que la habilita).
Las dos relaciones de D7 — `causado_por` y `justificado_por` — operan
en paralelo sobre la misma situación.

Salida: ../png/47_municipalidad_cadena_normativa.png
"""

import os
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

INK = "#1f2937"

# Colores
MULTA_FILL, MULTA_EDGE = "#fee2e2", "#b91c1c"     # rojo — la multa
CAUSAL_FILL, CAUSAL_EDGE = "#fef3c7", "#b45309"   # ámbar — causal
NORMA_FILL, NORMA_EDGE = "#dbeafe", "#1d4ed8"     # azul — normativo
RESOL_FILL, RESOL_EDGE = "#dcfce7", "#15803d"     # verde — resolución

fig, ax = plt.subplots(figsize=(14, 9.5), dpi=200)
ax.set_xlim(0, 14)
ax.set_ylim(0, 9.5)
ax.axis("off")
fig.patch.set_facecolor("#ffffff")

# Título
ax.text(7, 9.10,
        "La cadena normativa de una multa municipal: dos `por qué` en paralelo",
        ha="center", va="center", fontsize=14, fontweight="bold", color=INK)
ax.text(7, 8.70,
        "Una sola multa se conecta con su causa fáctica (la infracción) Y con la norma legal que la autoriza.",
        ha="center", va="center", fontsize=10, style="italic",
        color="#6b7280")
ax.text(7, 8.40,
        "D7 separa esos dos sentidos del 'porque' en relaciones distintas: causado_por y justificado_por.",
        ha="center", va="center", fontsize=10, style="italic",
        color="#6b7280")

# Helper para cajas
def caja(x, y, w, h, title, lines, fill, edge, title_size=10.5):
    box = FancyBboxPatch((x - w/2, y - h/2), w, h,
                         boxstyle="round,pad=0.05",
                         facecolor=fill, edgecolor=edge,
                         linewidth=1.7)
    ax.add_patch(box)
    ax.text(x, y + h/2 - 0.25, title,
            ha="center", va="center", fontsize=title_size,
            fontweight="bold", color=edge, family="monospace")
    for i, line in enumerate(lines):
        ax.text(x, y + 0.10 - i * 0.22, line,
                ha="center", va="center", fontsize=8,
                color="#374151")

# ─────────────────────────────────────────────────────────────
# La multa en el centro
# ─────────────────────────────────────────────────────────────
caja(7.0, 5.0, 3.6, 1.6, "multa_001",
     ["agente: policía municipal",
      "paciente: Juan",
      "monto: 450 USD",
      "momento: 08-Jul 14:35"],
     MULTA_FILL, MULTA_EDGE)

# ─────────────────────────────────────────────────────────────
# IZQUIERDA — cadena causal (la infracción)
# ─────────────────────────────────────────────────────────────
caja(2.0, 5.0, 3.2, 1.6, "infraccion_001",
     ["tipo: estac. prohibido",
      "lugar: Av. Principal",
      "momento: 08-Jul 14:32",
      "tema: vehículo de Juan"],
     CAUSAL_FILL, CAUSAL_EDGE)

# Flecha causa
arr = FancyArrowPatch((3.6, 5.0), (5.2, 5.0),
                      arrowstyle="-|>", mutation_scale=14,
                      color=CAUSAL_EDGE, linewidth=1.6)
ax.add_patch(arr)
ax.text(4.4, 5.32, "causado_por",
        ha="center", va="center", fontsize=9, fontweight="bold",
        color=CAUSAL_EDGE, family="monospace",
        bbox=dict(boxstyle="round,pad=0.18",
                  facecolor="white", edgecolor="none", alpha=0.95))

# ─────────────────────────────────────────────────────────────
# DERECHA — cadena normativa (el artículo y la ordenanza)
# ─────────────────────────────────────────────────────────────
caja(12.0, 5.0, 3.2, 1.6, "art_42_ord_158",
     ["artículo 42",
      "ordenanza 158-2023",
      "monto_multa: 450 USD",
      "(parte_de ordenanza)"],
     NORMA_FILL, NORMA_EDGE)

arr = FancyArrowPatch((10.4, 5.0), (8.8, 5.0),
                      arrowstyle="-|>", mutation_scale=14,
                      color=NORMA_EDGE, linewidth=1.6)
ax.add_patch(arr)
ax.text(9.6, 5.32, "justificado_por",
        ha="center", va="center", fontsize=9, fontweight="bold",
        color=NORMA_EDGE, family="monospace",
        bbox=dict(boxstyle="round,pad=0.18",
                  facecolor="white", edgecolor="none", alpha=0.95))

# ─────────────────────────────────────────────────────────────
# ARRIBA — la ordenanza completa (parte_de del artículo)
# ─────────────────────────────────────────────────────────────
caja(12.0, 7.4, 3.2, 1.0, "ord_158_2023",
     ["ordenanza_municipal",
      "vigente desde 2023-04-10"],
     NORMA_FILL, NORMA_EDGE)

arr_norma = FancyArrowPatch((12.0, 5.8), (12.0, 6.9),
                            arrowstyle="-|>", mutation_scale=12,
                            color=NORMA_EDGE, linewidth=1.4)
ax.add_patch(arr_norma)
ax.text(12.5, 6.4, "parte_de",
        ha="left", va="center", fontsize=8.5, fontweight="bold",
        color=NORMA_EDGE, family="monospace",
        bbox=dict(boxstyle="round,pad=0.15",
                  facecolor="white", edgecolor="none", alpha=0.9))

# ─────────────────────────────────────────────────────────────
# ABAJO — el recurso de reconsideración y la resolución
# ─────────────────────────────────────────────────────────────
caja(3.0, 2.3, 3.2, 1.3, "recurso_juan_001",
     ["agente: Juan",
      "tema: multa_001",
      "argumento: falta señalización"],
     "#f3e8ff", "#7c3aed")

arr_rec = FancyArrowPatch((4.6, 2.3), (5.4, 4.2),
                          arrowstyle="-|>", mutation_scale=12,
                          color="#7c3aed", linewidth=1.4,
                          connectionstyle="arc3,rad=0.15")
ax.add_patch(arr_rec)
ax.text(4.6, 3.3, "tema",
        ha="left", va="center", fontsize=8.5, fontweight="bold",
        color="#7c3aed", family="monospace",
        bbox=dict(boxstyle="round,pad=0.15",
                  facecolor="white", edgecolor="none", alpha=0.9))

caja(10.0, 2.3, 3.4, 1.3, "resolucion_001",
     ["agente: alcalde",
      "tema: recurso_juan_001",
      "conclusión: procedente"],
     RESOL_FILL, RESOL_EDGE)

arr_resol = FancyArrowPatch((8.4, 2.3), (6.6, 2.3),
                            arrowstyle="-|>", mutation_scale=12,
                            color=RESOL_EDGE, linewidth=1.4)
ax.add_patch(arr_resol)
ax.text(7.5, 2.58, "tema",
        ha="center", va="center", fontsize=8.5, fontweight="bold",
        color=RESOL_EDGE, family="monospace",
        bbox=dict(boxstyle="round,pad=0.15",
                  facecolor="white", edgecolor="none", alpha=0.9))

# Flecha de rectifica hacia la multa
arr_rect = FancyArrowPatch((10.0, 2.95), (8.5, 4.2),
                           arrowstyle="-|>", mutation_scale=12,
                           color=RESOL_EDGE, linewidth=1.4,
                           connectionstyle="arc3,rad=-0.20")
ax.add_patch(arr_rect)
ax.text(9.6, 3.4, "rectifica",
        ha="center", va="center", fontsize=8.5, fontweight="bold",
        color=RESOL_EDGE, family="monospace",
        bbox=dict(boxstyle="round,pad=0.15",
                  facecolor="white", edgecolor="none", alpha=0.9))

# Pie
ax.text(7, 0.55,
        "Toda acción del Estado conecta hacia atrás con una norma. La consulta `¿por qué se aplicó esta multa?`",
        ha="center", va="center", fontsize=9.5, color="#374151",
        style="italic")
ax.text(7, 0.28,
        "tiene dos respuestas válidas y distintas: la fáctica (causado_por) y la legal (justificado_por).",
        ha="center", va="center", fontsize=9.5, color="#374151",
        style="italic")

out = os.path.join(os.path.dirname(__file__), "..", "png",
                   "47_municipalidad_cadena_normativa.png")
plt.savefig(out, dpi=200, bbox_inches="tight", facecolor="#ffffff")
plt.close(fig)
print(f"  ✓ {out}")
