"""Diagrama: roadmap de los 6 frentes pendientes con prioridad y esfuerzo.

Cada frente como una caja con:
- prioridad (alta / media / baja)
- esfuerzo (semanas / meses / sostenido)
- qué desbloquea

Salida: ../png/39_roadmap_pendientes.png
"""

import os
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

INK = "#1f2937"

PRIO_COLORS = {
    "alta": "#b91c1c",
    "media": "#b45309",
    "baja": "#15803d",
    "sostenida": "#4f46e5",
}

fig, ax = plt.subplots(figsize=(15, 10), dpi=200)
ax.set_xlim(0, 15)
ax.set_ylim(0, 10)
ax.axis("off")
fig.patch.set_facecolor("#ffffff")

# Título
ax.text(7.5, 9.55,
        "Roadmap: seis frentes entre el prototipo y la infraestructura",
        ha="center", va="center", fontsize=14, fontweight="bold", color=INK)
ax.text(7.5, 9.15,
        "Cada frente con su prioridad, esfuerzo estimado y dependencia.",
        ha="center", va="center", fontsize=10, style="italic", color="#6b7280")

# 6 frentes en 2x3
frentes = [
    {
        "n": "1", "name": "Motor de inferencia",
        "prio": "alta",
        "effort": "3-6 meses",
        "what": "SHACL · Datalog · custom · LLM",
        "unblocks": "ejecutar reglas declarativas",
    },
    {
        "n": "2", "name": "Bitemporalidad completa",
        "prio": "alta",
        "effort": "1 mes",
        "what": "valid time + transaction time",
        "unblocks": "\"¿qué sabíamos cuándo?\" auditable",
    },
    {
        "n": "3", "name": "Persistencia industrial",
        "prio": "alta",
        "effort": "2-3 meses",
        "what": "SQLite · Postgres · Kùzu · RDF",
        "unblocks": "uso fuera del prototipo en memoria",
    },
    {
        "n": "4", "name": "Tooling",
        "prio": "media",
        "effort": "3-6 meses",
        "what": "ingestor · parser · IDE · MCP gen",
        "unblocks": "adopción sin escribir glue code",
    },
    {
        "n": "5", "name": "Lexicon poblado",
        "prio": "sostenida",
        "effort": "trabajo continuo",
        "what": "miles de verbos por idioma",
        "unblocks": "usabilidad real en producción",
    },
    {
        "n": "6", "name": "Comunidad",
        "prio": "alta",
        "effort": "2-5 años",
        "what": "repo · proceso · foros · estándares",
        "unblocks": "que el proyecto sobreviva al autor",
    },
]

box_w, box_h = 4.4, 2.4
positions = [
    (2.7, 6.6), (7.5, 6.6), (12.3, 6.6),
    (2.7, 3.4), (7.5, 3.4), (12.3, 3.4),
]

for f, (x, y) in zip(frentes, positions):
    color = PRIO_COLORS[f["prio"]]
    box = FancyBboxPatch((x - box_w/2, y - box_h/2), box_w, box_h,
                         boxstyle="round,pad=0.05",
                         facecolor="white", edgecolor=color, linewidth=2.0)
    ax.add_patch(box)

    # número en círculo
    chip = FancyBboxPatch((x - box_w/2 + 0.18, y + box_h/2 - 0.50), 0.42, 0.42,
                          boxstyle="round,pad=0.02",
                          facecolor=color, edgecolor="none")
    ax.add_patch(chip)
    ax.text(x - box_w/2 + 0.39, y + box_h/2 - 0.29, f["n"],
            ha="center", va="center", fontsize=11,
            color="white", fontweight="bold", family="monospace")

    # nombre
    ax.text(x, y + box_h/2 - 0.30, f["name"],
            ha="center", va="center", fontsize=11.5, fontweight="bold",
            color=color)

    # chip prioridad
    pchip = FancyBboxPatch((x - 0.95, y + box_h/2 - 0.85), 1.9, 0.30,
                           boxstyle="round,pad=0.02",
                           facecolor=color, edgecolor="none")
    ax.add_patch(pchip)
    ax.text(x, y + box_h/2 - 0.70,
            f"prioridad: {f['prio']}",
            ha="center", va="center", fontsize=8.5,
            color="white", fontweight="bold")

    # esfuerzo
    ax.text(x, y + box_h/2 - 1.20,
            f"esfuerzo: {f['effort']}",
            ha="center", va="center", fontsize=8.5,
            color="#374151")

    # qué
    ax.text(x, y - 0.20, "qué:",
            ha="center", va="center", fontsize=8,
            color="#6b7280", fontweight="bold")
    ax.text(x, y - 0.45, f["what"],
            ha="center", va="center", fontsize=8.5,
            color="#374151", family="monospace")

    # desbloquea
    ax.text(x, y - 0.80, "desbloquea:",
            ha="center", va="center", fontsize=8,
            color="#6b7280", fontweight="bold")
    ax.text(x, y - 1.05, f["unblocks"],
            ha="center", va="center", fontsize=8.5,
            color="#374151", style="italic")

# Pie / leyenda
ax.text(7.5, 1.30,
        "Frentes 1-3 son técnicos y acotados; los hace un equipo chico en seis meses.",
        ha="center", va="center", fontsize=9.5, color="#374151")
ax.text(7.5, 1.00,
        "El 4 (tooling) acelera adopción. El 5 (lexicon) es trabajo lingüístico sostenido. El 6 (comunidad) es el más decisivo.",
        ha="center", va="center", fontsize=9.5, style="italic", color="#374151")

# Mini leyenda de colores
ax.text(0.5, 0.45, "Prioridad:",
        ha="left", va="center", fontsize=9, fontweight="bold", color="#374151")
xleg = 2.0
for label, color in [("alta", "#b91c1c"), ("media", "#b45309"),
                     ("sostenida", "#4f46e5")]:
    chip = FancyBboxPatch((xleg, 0.30), 0.35, 0.30,
                          boxstyle="round,pad=0.02",
                          facecolor=color, edgecolor="none")
    ax.add_patch(chip)
    ax.text(xleg + 0.50, 0.45, label,
            ha="left", va="center", fontsize=9, color="#6b7280")
    xleg += 2.4

out = os.path.join(os.path.dirname(__file__), "..", "png",
                   "39_roadmap_pendientes.png")
plt.savefig(out, dpi=200, bbox_inches="tight", facecolor="#ffffff")
plt.close(fig)
print(f"  ✓ {out}")
