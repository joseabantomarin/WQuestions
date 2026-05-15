"""Diagrama: matriz comparativa de los 4 dominios estresantes.

Música / Química / Fútbol / Contrato vs aspectos que estresan al modelo.

Salida: ../png/33_cuatro_dominios.png
"""

import os
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

INK = "#1f2937"

# Colores por dominio
DOMS = [
    {"name": "Música",   "fill": "#dbeafe", "edge": "#1d4ed8",
     "central": "recursión categórica",
     "ejemplo": "Sonata Op. 27 nº 2",
     "items": [
         "K profundo: sonata ⊃ movimientos ⊃ secciones ⊃ frases",
         "obra como K, interpretación como O",
         "tiempo musical (compás) no es T absoluto",
         "fricción: tema rechaza K → patch rol de dominio",
     ]},
    {"name": "Química",  "fill": "#fef3c7", "edge": "#b45309",
     "central": "D5 al extremo",
     "ejemplo": "Combustión del metano",
     "items": [
         "sin agente humano: el grafo lo acepta",
         "plantilla K + instancia O con factor de escala",
         "cantidades estequiométricas como N + K (unidad)",
         "fricción: paciente: O → Q demasiado estrecho",
     ]},
    {"name": "Fútbol",   "fill": "#dcfce7", "edge": "#15803d",
     "central": "concurrencia + estado derivado",
     "ejemplo": "Argentina-Perú 2026",
     "items": [
         "22 jugadores en paralelo: granularidad opcional",
         "dos relojes: T absoluto + minuto_partido",
         "marcador como agregación de hechos primitivos",
         "fricción: partes: O → Q (debería ser → V)",
     ]},
    {"name": "Contrato", "fill": "#fee2e2", "edge": "#b91c1c",
     "central": "lo normativo manda",
     "ejemplo": "Alquiler 12 meses",
     "items": [
         "vigencia + cláusulas con condición/consecuente",
         "justificado_por preserva la cadena argumentativa",
         "hechos inmutables: cambios = situaciones nuevas",
         "fricción: bitemporalidad completa pendiente",
     ]},
]

fig, ax = plt.subplots(figsize=(15, 10), dpi=200)
ax.set_xlim(0, 15)
ax.set_ylim(0, 10)
ax.axis("off")
fig.patch.set_facecolor("#ffffff")

# Título
ax.text(7.5, 9.55, "Cuatro dominios que estresan al modelo, cada uno por una razón distinta",
        ha="center", va="center", fontsize=14, fontweight="bold", color=INK)
ax.text(7.5, 9.15,
        "El test de un modelo universal: pasar por dominios cualitativamente diferentes y ver dónde se dobla.",
        ha="center", va="center", fontsize=10, style="italic", color="#6b7280")

# 2x2 grid de dominios
positions = [(3.75, 6.0), (11.25, 6.0), (3.75, 2.4), (11.25, 2.4)]
box_w, box_h = 6.6, 3.2

for (x, y), dom in zip(positions, DOMS):
    box = FancyBboxPatch((x - box_w/2, y - box_h/2), box_w, box_h,
                         boxstyle="round,pad=0.05",
                         facecolor=dom["fill"], edgecolor=dom["edge"],
                         linewidth=1.8)
    ax.add_patch(box)

    # Encabezado: nombre + central + ejemplo
    ax.text(x - box_w/2 + 0.3, y + box_h/2 - 0.40, dom["name"],
            ha="left", va="center", fontsize=15, fontweight="bold",
            color=dom["edge"], family="monospace")
    ax.text(x + box_w/2 - 0.3, y + box_h/2 - 0.40,
            f"({dom['ejemplo']})",
            ha="right", va="center", fontsize=8.5,
            style="italic", color=dom["edge"])
    ax.text(x, y + box_h/2 - 0.85,
            "lo que estresa: " + dom["central"],
            ha="center", va="center", fontsize=10, fontweight="bold",
            color=dom["edge"])

    # Línea separadora
    ax.plot([x - box_w/2 + 0.3, x + box_w/2 - 0.3],
            [y + box_h/2 - 1.05, y + box_h/2 - 1.05],
            color=dom["edge"], lw=0.8, alpha=0.4)

    # Items
    for i, item in enumerate(dom["items"]):
        ax.text(x - box_w/2 + 0.5,
                y + box_h/2 - 1.40 - i * 0.40,
                f"• {item}",
                ha="left", va="center", fontsize=9, color="#374151")

# Pie
ax.text(7.5, 0.35,
        "Resultado: cero rompimientos. Cuatro fricciones documentadas con patch propuesto o trabajo pendiente.",
        ha="center", va="center", fontsize=10, style="italic", color="#374151")

out = os.path.join(os.path.dirname(__file__), "..", "png",
                   "33_cuatro_dominios.png")
plt.savefig(out, dpi=200, bbox_inches="tight", facecolor="#ffffff")
plt.close(fig)
print(f"  ✓ {out}")
