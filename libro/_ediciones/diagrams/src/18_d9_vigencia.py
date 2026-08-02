"""Diagrama: D9 — vigencia temporal.
La residencia de Marta como dos situaciones sucesivas, cada una con su rango.
Consultas temporales recuperan la situación válida en el momento solicitado.

Salida: ../png/18_d9_vigencia.png
"""

import os
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, FancyArrowPatch

INK = "#1f2937"

fig, ax = plt.subplots(figsize=(13, 7.5), dpi=200)
ax.set_xlim(0, 13)
ax.set_ylim(0, 7.5)
ax.axis("off")
fig.patch.set_facecolor("#ffffff")

# Título
ax.text(6.5, 7.15, "D9 — vigencia temporal mediante reificación",
        ha="center", va="center", fontsize=14, fontweight="bold", color=INK)
ax.text(6.5, 6.75,
        "La residencia de Marta a través del tiempo: cada valor es una situación con su rango de validez.",
        ha="center", va="center", fontsize=10, style="italic", color="#6b7280")

# Línea de tiempo
TL_Y = 1.0
TL_LEFT = 0.8
TL_RIGHT = 12.2
ax.annotate("", xy=(TL_RIGHT, TL_Y), xytext=(TL_LEFT, TL_Y),
            arrowprops=dict(arrowstyle="->", color="#6b7280", lw=1.4))
# Marcas anuales
years = [(2010, 1.2), (2015, 3.5), (2020, 5.8), (2025, 8.6), (2030, 11.4)]
for year, x in years:
    ax.plot([x, x], [TL_Y - 0.08, TL_Y + 0.08], color="#9ca3af", linewidth=0.8)
    ax.text(x, TL_Y - 0.25, str(year), ha="center", va="center",
            fontsize=9, color="#6b7280")

# Función para mapear año a posición x
def x_of(year):
    # 2010 → 1.2, 2030 → 11.4; lineal
    return 1.2 + (year - 2010) * (11.4 - 1.2) / 20

# Banda residencia_001 (2010-03 a 2025-12)
band1_x0 = x_of(2010.25)
band1_x1 = x_of(2026.0)
band1_y = 2.7
band1 = Rectangle((band1_x0, band1_y), band1_x1 - band1_x0, 0.8,
                  facecolor="#dbeafe", edgecolor="#1d4ed8", linewidth=1.6)
ax.add_patch(band1)
ax.text((band1_x0 + band1_x1)/2, band1_y + 0.55, "residencia_001",
        ha="center", va="center", fontsize=11, fontweight="bold",
        color="#1d4ed8", family="monospace")
ax.text((band1_x0 + band1_x1)/2, band1_y + 0.25,
        "sujeto: marta · ciudad: ciudad_a",
        ha="center", va="center", fontsize=9, color=INK, family="monospace")

# Banda residencia_002 (2026 hasta hoy)
band2_x0 = x_of(2026.0)
band2_x1 = x_of(2029.0)  # representa "hoy"
band2_y = 2.7
band2 = Rectangle((band2_x0, band2_y), band2_x1 - band2_x0, 0.8,
                  facecolor="#dcfce7", edgecolor="#15803d", linewidth=1.6)
ax.add_patch(band2)
ax.text((band2_x0 + band2_x1)/2, band2_y + 0.55, "residencia_002",
        ha="center", va="center", fontsize=11, fontweight="bold",
        color="#15803d", family="monospace")
ax.text((band2_x0 + band2_x1)/2, band2_y + 0.25,
        "sujeto: marta · ciudad: ciudad_b",
        ha="center", va="center", fontsize=9, color=INK, family="monospace")
# Flecha que indica "abierto" hacia el futuro
ax.annotate("", xy=(band2_x1 + 0.3, band2_y + 0.4),
            xytext=(band2_x1, band2_y + 0.4),
            arrowprops=dict(arrowstyle="->", color="#15803d", lw=1.5))
ax.text(band2_x1 + 0.5, band2_y + 0.4, "fin: null",
        ha="left", va="center", fontsize=8, style="italic", color="#15803d")

# Líneas verticales que conectan los rangos con la línea de tiempo
for x_val in [band1_x0, band1_x1]:
    ax.plot([x_val, x_val], [TL_Y, band1_y], color="#1d4ed8",
            linewidth=0.6, linestyle=":", alpha=0.5)
for x_val in [band2_x0]:
    ax.plot([x_val, x_val], [TL_Y, band2_y], color="#15803d",
            linewidth=0.6, linestyle=":", alpha=0.5)

# Etiquetas inicio/fin
ax.text(band1_x0, band1_y + 0.95, "inicio:\n2010-03-15",
        ha="center", va="bottom", fontsize=8, color="#1d4ed8")
ax.text(band1_x1, band1_y + 0.95, "fin:\n2025-12-31",
        ha="center", va="bottom", fontsize=8, color="#1d4ed8")
ax.text(band2_x0, band2_y + 0.95, "inicio:\n2026-01-01",
        ha="center", va="bottom", fontsize=8, color="#15803d")

# Ejemplo de consulta temporal
query_x = x_of(2018)
ax.plot([query_x, query_x], [TL_Y, 6.0], color="#b91c1c",
        linewidth=1.5, linestyle="--", alpha=0.85)
ax.plot([query_x], [TL_Y], "v", color="#b91c1c", markersize=10)
ax.text(query_x, 6.25, "Consulta: ¿dónde vivía\nMarta en 2018?",
        ha="center", va="bottom", fontsize=9, fontweight="bold",
        color="#b91c1c")

# Caja con la respuesta
ans_box = FancyBboxPatch((query_x - 1.2, 5.0), 2.4, 0.7,
                         boxstyle="round,pad=0.04",
                         facecolor="#fee2e2", edgecolor="#b91c1c", linewidth=1.3)
ax.add_patch(ans_box)
ax.text(query_x, 5.45, "→ ciudad_a",
        ha="center", va="center", fontsize=10, fontweight="bold",
        color="#b91c1c", family="monospace")
ax.text(query_x, 5.15, "(residencia_001)",
        ha="center", va="center", fontsize=8, style="italic", color="#7f1d1d")

# Otro ejemplo de consulta
query2_x = x_of(2027.5)
ax.plot([query2_x, query2_x], [TL_Y, 6.0], color="#1e40af",
        linewidth=1.5, linestyle="--", alpha=0.85)
ax.plot([query2_x], [TL_Y], "v", color="#1e40af", markersize=10)
ax.text(query2_x, 6.25, "¿Dónde vive ahora?",
        ha="center", va="bottom", fontsize=9, fontweight="bold",
        color="#1e40af")

ans_box2 = FancyBboxPatch((query2_x - 1.2, 5.0), 2.4, 0.7,
                          boxstyle="round,pad=0.04",
                          facecolor="#dbeafe", edgecolor="#1e40af", linewidth=1.3)
ax.add_patch(ans_box2)
ax.text(query2_x, 5.45, "→ ciudad_b",
        ha="center", va="center", fontsize=10, fontweight="bold",
        color="#1e40af", family="monospace")
ax.text(query2_x, 5.15, "(residencia_002)",
        ha="center", va="center", fontsize=8, style="italic", color="#1e3a8a")

# Pie
ax.text(6.5, 0.20,
        "Sin D9: el valor nuevo sobreescribe al anterior. Con D9: ambos rangos coexisten y la consulta\n"
        "temporal recupera el correcto según el momento solicitado.",
        ha="center", va="center", fontsize=9.5, style="italic", color="#6b7280")

out = os.path.join(os.path.dirname(__file__), "..", "png",
                   "18_d9_vigencia.png")
plt.savefig(out, dpi=200, bbox_inches="tight", facecolor="#ffffff")
plt.close(fig)
print(f"  ✓ {out}")
