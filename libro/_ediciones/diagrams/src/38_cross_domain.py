"""Diagrama: consulta cross-dominio en acción.

Un periodista pregunta y el LLM combina tres consultas sobre tres
dominios distintos (noticias políticas, indicadores macroeconómicos,
ventas trimestrales), produciendo una respuesta narrativa trazable.

Salida: ../png/38_cross_domain.png
"""

import os
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

INK = "#1f2937"

fig, ax = plt.subplots(figsize=(15, 9), dpi=200)
ax.set_xlim(0, 15)
ax.set_ylim(0, 9)
ax.axis("off")
fig.patch.set_facecolor("#ffffff")

# Título
ax.text(7.5, 8.55,
        "Una consulta cross-dominio real en acción",
        ha="center", va="center", fontsize=14, fontweight="bold", color=INK)
ax.text(7.5, 8.15,
        "Tres dominios, tres dialectos, un solo grafo. El LLM compone; la respuesta es trazable a hechos.",
        ha="center", va="center", fontsize=10, style="italic", color="#6b7280")

# Usuario (arriba izquierda)
user_box = FancyBboxPatch((0.4, 6.6), 5.2, 1.4,
                          boxstyle="round,pad=0.06",
                          facecolor="#fef3c7", edgecolor="#b45309",
                          linewidth=1.6)
ax.add_patch(user_box)
ax.text(0.7, 7.65, "PERIODISTA",
        ha="left", va="center", fontsize=10, fontweight="bold",
        color="#b45309")
ax.text(3.0, 7.30,
        "\"¿Cómo afectó la reforma tributaria de 2024",
        ha="center", va="center", fontsize=9.5, style="italic",
        color="#374151")
ax.text(3.0, 7.00,
        "a las ventas del sector retail?\"",
        ha="center", va="center", fontsize=9.5, style="italic",
        color="#374151")

# LLM (arriba derecha)
llm_box = FancyBboxPatch((9.0, 6.6), 5.6, 1.4,
                         boxstyle="round,pad=0.06",
                         facecolor="#dbeafe", edgecolor="#1d4ed8",
                         linewidth=1.8)
ax.add_patch(llm_box)
ax.text(9.3, 7.65, "LLM",
        ha="left", va="center", fontsize=10, fontweight="bold",
        color="#1d4ed8")
ax.text(11.8, 7.30,
        "Plan: 3 consultas paralelas",
        ha="center", va="center", fontsize=9,
        color="#374151")
ax.text(11.8, 7.00,
        "+ correlación temporal + síntesis narrativa",
        ha="center", va="center", fontsize=8.5, style="italic",
        color="#374151")

# Flecha usuario → LLM
arr = FancyArrowPatch((5.6, 7.3), (9.0, 7.3),
                      arrowstyle="-|>", mutation_scale=14,
                      color="#6b7280", linewidth=1.4)
ax.add_patch(arr)

# Tres dominios en una fila
domains = [
    {
        "x": 2.5, "title": "Dominio: política",
        "fill": "#fee2e2", "edge": "#b91c1c",
        "query": "type: noticia_politica",
        "filter": "tema: impuesto_consumo",
        "result": "→ 47 noticias\n  2024-Q1 a 2024-Q3",
    },
    {
        "x": 7.5, "title": "Dominio: macro",
        "fill": "#fef3c7", "edge": "#b45309",
        "query": "type: indicador_macro",
        "filter": "sector: retail",
        "result": "→ 12 trimestres\n  con elasticidad",
    },
    {
        "x": 12.5, "title": "Dominio: ventas",
        "fill": "#dcfce7", "edge": "#15803d",
        "query": "type: agregado_trimestral",
        "filter": "sector: retail",
        "result": "→ caída 8%\n  en 2024-Q3",
    },
]

for d in domains:
    box = FancyBboxPatch((d["x"] - 2.0, 3.4), 4.0, 2.3,
                         boxstyle="round,pad=0.05",
                         facecolor=d["fill"], edgecolor=d["edge"],
                         linewidth=1.6)
    ax.add_patch(box)
    ax.text(d["x"], 5.40, d["title"],
            ha="center", va="center", fontsize=11, fontweight="bold",
            color=d["edge"])
    # Query
    ax.text(d["x"], 5.00, "query(Pattern(",
            ha="center", va="center", fontsize=8.5,
            color="#374151", family="monospace")
    ax.text(d["x"], 4.75, d["query"] + ",",
            ha="center", va="center", fontsize=8,
            color="#374151", family="monospace")
    ax.text(d["x"], 4.50, d["filter"],
            ha="center", va="center", fontsize=8,
            color="#374151", family="monospace")
    ax.text(d["x"], 4.25, "))",
            ha="center", va="center", fontsize=8.5,
            color="#374151", family="monospace")
    # Result
    box2 = FancyBboxPatch((d["x"] - 1.7, 3.50), 3.4, 0.55,
                          boxstyle="round,pad=0.04",
                          facecolor="white", edgecolor=d["edge"],
                          linewidth=1.0)
    ax.add_patch(box2)
    for j, line in enumerate(d["result"].split("\n")):
        ax.text(d["x"], 3.92 - j * 0.20, line,
                ha="center", va="center", fontsize=8.5,
                color=d["edge"], family="monospace")

    # Flecha LLM → cada dominio
    arr = FancyArrowPatch((11.5, 6.6), (d["x"], 5.7),
                          arrowstyle="-|>", mutation_scale=10,
                          color="#9ca3af", linewidth=0.9,
                          linestyle="dashed")
    ax.add_patch(arr)

# Respuesta narrativa final
resp_box = FancyBboxPatch((1.5, 0.85), 12.0, 1.95,
                          boxstyle="round,pad=0.06",
                          facecolor="#f9fafb", edgecolor="#1d4ed8",
                          linewidth=1.6)
ax.add_patch(resp_box)
ax.text(2.0, 2.55, "RESPUESTA DEL LLM",
        ha="left", va="center", fontsize=10, fontweight="bold",
        color="#1d4ed8")
ax.text(7.5, 2.20,
        "\"La reforma tributaria, aprobada en marzo 2024 (47 noticias trazadas), elevó el impuesto al consumo del 18% al 21%.",
        ha="center", va="center", fontsize=9,
        color="#374151")
ax.text(7.5, 1.92,
        "Las ventas del sector retail cayeron 8% en el tercer trimestre de 2024 respecto al primero,",
        ha="center", va="center", fontsize=9,
        color="#374151")
ax.text(7.5, 1.64,
        "consistente con la elasticidad estimada de -0.4 por cada punto porcentual de impuesto.\"",
        ha="center", va="center", fontsize=9,
        color="#374151")
ax.text(7.5, 1.20,
        "Trazabilidad: cada afirmación se vincula a hechos atómicos del grafo, citables por momento, dominio y fuente.",
        ha="center", va="center", fontsize=8.5,
        style="italic", color="#6b7280")

# Flechas desde los 3 dominios a la respuesta
for d in domains:
    arr = FancyArrowPatch((d["x"], 3.4), (7.5, 2.80),
                          arrowstyle="-|>", mutation_scale=10,
                          color=d["edge"], linewidth=0.9, alpha=0.6)
    ax.add_patch(arr)

out = os.path.join(os.path.dirname(__file__), "..", "png",
                   "38_cross_domain.png")
plt.savefig(out, dpi=200, bbox_inches="tight", facecolor="#ffffff")
plt.close(fig)
print(f"  ✓ {out}")
