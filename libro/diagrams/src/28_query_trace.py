"""Diagrama: una consulta WH como recorrido del grafo.

Muestra cómo `count(u, Pattern(fixed={...}, type_constraint=K))` se
procesa: arranca con un filtro por tipo, descarta sujetos que no
cumplen los roles fijos, y agrega lo que queda.

Salida: ../png/28_query_trace.png
"""

import os
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

INK = "#1f2937"
O_FILL, O_EDGE = "#dcfce7", "#15803d"
Q_FILL, Q_EDGE = "#dbeafe", "#1d4ed8"
K_FILL, K_EDGE = "#e0e7ff", "#4f46e5"

fig, ax = plt.subplots(figsize=(15, 9.5), dpi=200)
ax.set_xlim(0, 15)
ax.set_ylim(0, 9.5)
ax.axis("off")
fig.patch.set_facecolor("#ffffff")

# Título
ax.text(7.5, 9.10,
        "Una consulta como recorrido del grafo: ¿Cuántas sesiones finalizadas tiene Ana?",
        ha="center", va="center", fontsize=14, fontweight="bold", color=INK)
ax.text(7.5, 8.70,
        "El patrón fija dos roles, restringe por tipo, y agrega los matches.",
        ha="center", va="center", fontsize=10, style="italic", color="#6b7280")

# ----- Patrón (entrada) -----
pat_box = FancyBboxPatch((0.7, 6.7), 4.5, 1.6,
                         boxstyle="round,pad=0.05",
                         facecolor="#f9fafb", edgecolor="#9ca3af",
                         linewidth=1.4)
ax.add_patch(pat_box)
ax.text(2.95, 8.10, "Pattern",
        ha="center", va="center", fontsize=11.5, fontweight="bold",
        color=INK, family="monospace")
ax.text(0.95, 7.75, "type_constraint:",
        ha="left", va="center", fontsize=9,
        color="#374151", family="monospace")
ax.text(2.85, 7.75, "servicio_sauna",
        ha="left", va="center", fontsize=9,
        color=K_EDGE, family="monospace", fontweight="bold")

ax.text(0.95, 7.40, "fixed.cliente:",
        ha="left", va="center", fontsize=9,
        color="#374151", family="monospace")
ax.text(2.85, 7.40, "ana",
        ha="left", va="center", fontsize=9,
        color=Q_EDGE, family="monospace", fontweight="bold")

ax.text(0.95, 7.05, "fixed.estatus_factual:",
        ha="left", va="center", fontsize=9,
        color="#374151", family="monospace")
ax.text(3.40, 7.05, "finalizada",
        ha="left", va="center", fontsize=9,
        color=K_EDGE, family="monospace", fontweight="bold")

# ----- Paso 1: candidatos por tipo -----
ax.text(7.5, 7.95, "Paso 1 — sujetos en O con instancia_de = servicio_sauna",
        ha="center", va="center", fontsize=10.5, fontweight="bold", color=INK)
candidates_y = 7.30
cand_x = [6.5, 7.7, 8.9, 10.1, 11.3, 12.5, 13.7]
cand_labels = ["sesion_01", "sesion_02", "sesion_03", "sesion_04",
               "...", "sesion_16", "intencion_001"]
for x, lb in zip(cand_x, cand_labels):
    box = FancyBboxPatch((x - 0.55, candidates_y - 0.30), 1.1, 0.55,
                         boxstyle="round,pad=0.03",
                         facecolor=O_FILL, edgecolor=O_EDGE, linewidth=1.0)
    ax.add_patch(box)
    ax.text(x, candidates_y, lb,
            ha="center", va="center", fontsize=8,
            color=O_EDGE, family="monospace")
ax.text(7.5, candidates_y - 0.6,
        "(16 sesiones de los 3 clientes + algunas otras situaciones)",
        ha="center", va="center", fontsize=8, style="italic", color="#6b7280")

# Flecha del patrón al paso 1
ax.annotate("", xy=(5.7, candidates_y + 0.1), xytext=(5.2, 7.6),
            arrowprops=dict(arrowstyle="-|>", color="#9ca3af", lw=1.2))

# ----- Paso 2: filtrar por cliente=ana -----
ax.text(7.5, 5.85, "Paso 2 — filtrar candidatos cuyo cliente = ana",
        ha="center", va="center", fontsize=10.5, fontweight="bold", color=INK)
p2_y = 5.20
p2_x = [7.0, 8.3, 9.6, 10.9, 12.2, 13.5]
p2_labels = ["sesion_ana_01", "sesion_ana_02", "sesion_ana_03",
             "sesion_ana_04", "...", "sesion_ana_08"]
for x, lb in zip(p2_x, p2_labels):
    box = FancyBboxPatch((x - 0.60, p2_y - 0.30), 1.2, 0.55,
                         boxstyle="round,pad=0.03",
                         facecolor=O_FILL, edgecolor=O_EDGE, linewidth=1.2)
    ax.add_patch(box)
    ax.text(x, p2_y, lb,
            ha="center", va="center", fontsize=8,
            color=O_EDGE, family="monospace", fontweight="bold")

# Descartados (paso 2)
ax.text(2.5, 5.20, "Descartadas:",
        ha="left", va="center", fontsize=9, fontweight="bold", color="#9ca3af")
ax.text(2.5, 4.85,
        "• sesiones de Beto (6)",
        ha="left", va="center", fontsize=8.5,
        color="#9ca3af", family="monospace")
ax.text(2.5, 4.60,
        "• sesiones de Carlos (2)",
        ha="left", va="center", fontsize=8.5,
        color="#9ca3af", family="monospace")
ax.text(2.5, 4.35,
        "• otras situaciones no-sesión",
        ha="left", va="center", fontsize=8.5,
        color="#9ca3af", family="monospace")

# Flecha del paso 1 al paso 2
ax.annotate("", xy=(7.5, p2_y + 0.4), xytext=(7.5, candidates_y - 0.40),
            arrowprops=dict(arrowstyle="-|>", color="#9ca3af", lw=1.2))

# ----- Paso 3: filtrar por estatus_factual=finalizada -----
ax.text(7.5, 3.45, "Paso 3 — filtrar por estatus_factual = finalizada",
        ha="center", va="center", fontsize=10.5, fontweight="bold", color=INK)
p3_y = 2.80
p3_x = [7.0, 8.3, 9.6, 10.9, 12.2, 13.5]
for x, lb in zip(p3_x, p2_labels):
    box = FancyBboxPatch((x - 0.60, p3_y - 0.30), 1.2, 0.55,
                         boxstyle="round,pad=0.03",
                         facecolor="#bbf7d0", edgecolor=O_EDGE, linewidth=1.5)
    ax.add_patch(box)
    ax.text(x, p3_y, lb,
            ha="center", va="center", fontsize=8,
            color=O_EDGE, family="monospace", fontweight="bold")

# Flecha del paso 2 al paso 3
ax.annotate("", xy=(7.5, p3_y + 0.40), xytext=(7.5, p2_y - 0.40),
            arrowprops=dict(arrowstyle="-|>", color="#9ca3af", lw=1.2))

# ----- Resultado -----
res_box = FancyBboxPatch((1.0, 1.0), 4.5, 1.4,
                         boxstyle="round,pad=0.05",
                         facecolor="#fef3c7", edgecolor="#b45309",
                         linewidth=1.8)
ax.add_patch(res_box)
ax.text(3.25, 2.10, "count() = 8",
        ha="center", va="center", fontsize=14, fontweight="bold",
        color="#b45309", family="monospace")
ax.text(3.25, 1.65, "Ana cumple la regla \"7 visitas → 1 gratis\"",
        ha="center", va="center", fontsize=9.5, color="#92400e",
        style="italic")
ax.text(3.25, 1.30, "(evaluador externo: 8 ≥ 7 → True)",
        ha="center", va="center", fontsize=8.5,
        color="#92400e", family="monospace")

# Flecha del paso 3 al resultado
arr = FancyArrowPatch((7.5, p3_y - 0.40), (5.5, 1.7),
                      arrowstyle="-|>", mutation_scale=15,
                      color="#b45309", linewidth=1.5,
                      connectionstyle="arc3,rad=0.15")
ax.add_patch(arr)

# Pie
ax.text(10.5, 1.3,
        "El motor de consulta no entiende de saunas:\n"
        "solo recorre los hechos atómicos guiado por el patrón.\n"
        "La regla de fidelidad la aplica código aplicación encima.",
        ha="left", va="center", fontsize=9.5, style="italic", color="#374151")

out = os.path.join(os.path.dirname(__file__), "..", "png",
                   "28_query_trace.png")
plt.savefig(out, dpi=200, bbox_inches="tight", facecolor="#ffffff")
plt.close(fig)
print(f"  ✓ {out}")
