"""Diagrama: la consulta médica como entidad articuladora con 5 sub-situaciones.

Salida: ../png/31_consulta_clinica.png
"""

import os
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

INK = "#1f2937"
O_FILL, O_EDGE = "#dcfce7", "#15803d"

fig, ax = plt.subplots(figsize=(15, 9), dpi=200)
ax.set_xlim(0, 15)
ax.set_ylim(0, 9)
ax.axis("off")
fig.patch.set_facecolor("#ffffff")

# Título
ax.text(7.5, 8.55, "La consulta médica como entidad articuladora",
        ha="center", va="center", fontsize=14, fontweight="bold", color=INK)
ax.text(7.5, 8.15,
        "Cinco sub-situaciones reificadas cuelgan de la consulta. Cada una tiene su propia estructura semántica.",
        ha="center", va="center", fontsize=10, style="italic", color="#6b7280")

# Centro: la consulta
cx, cy = 7.5, 5.0
con_box = FancyBboxPatch((cx - 2.2, cy - 0.75), 4.4, 1.5,
                         boxstyle="round,pad=0.06",
                         facecolor="#dcfce7", edgecolor=O_EDGE, linewidth=2.8)
ax.add_patch(con_box)
ax.text(cx, cy + 0.40, "consulta_001",
        ha="center", va="center", fontsize=13.5, fontweight="bold",
        color=O_EDGE, family="monospace")
ax.text(cx, cy + 0.10, "∈ O · consulta_medica",
        ha="center", va="center", fontsize=9, style="italic", color="#6b7280")
ax.text(cx, cy - 0.20,
        "agente: Dra. Torres · paciente: María",
        ha="center", va="center", fontsize=8.5,
        color="#374151", family="monospace")
ax.text(cx, cy - 0.45,
        "momento: 2026-05-14 10:30 · motivo: cefalea",
        ha="center", va="center", fontsize=8.5,
        color="#374151", family="monospace")

# 5 sub-situaciones alrededor
subs = [
    {"label": "sintoma_001",
     "details": ["instancia_de: cefalea_persistente",
                 "experimentador: María",
                 "momento: 3 días antes"],
     "x": 2.0, "y": 7.5},
    {"label": "medicion_pa_001",
     "details": ["medida_de: presión_arterial",
                 "monto: 145/92 mmHg",
                 "agente: Dra. Torres"],
     "x": 13.0, "y": 7.5},
    {"label": "diag_hta_001",
     "details": ["diagnosticado_como: HTA grado 1",
                 "modalidad: epistémica",
                 "estatus_factual: confirmado",
                 "tema: medicion_pa_001"],
     "x": 1.7, "y": 2.5},
    {"label": "pres_001",
     "details": ["medicamento_prescrito: enalapril 10mg",
                 "frecuencia: cada mañana",
                 "motivado_por: diag_hta_001",
                 "con_finalidad: objetivo_reducir_PA"],
     "x": 7.5, "y": 1.8},
    {"label": "control_001",
     "details": ["paciente: María",
                 "momento: 2026-06-13",
                 "estatus_factual: previsto"],
     "x": 13.3, "y": 2.5},
]

for s in subs:
    x, y = s["x"], s["y"]
    nd = len(s["details"])
    h = 0.35 + nd * 0.22
    box = FancyBboxPatch((x - 1.65, y - h/2), 3.3, h,
                         boxstyle="round,pad=0.04",
                         facecolor="#f0fdf4", edgecolor=O_EDGE, linewidth=1.5)
    ax.add_patch(box)
    ax.text(x, y + h/2 - 0.20, s["label"],
            ha="center", va="center", fontsize=10, fontweight="bold",
            color=O_EDGE, family="monospace")
    for j, d in enumerate(s["details"]):
        ax.text(x, y + h/2 - 0.45 - j * 0.22, d,
                ha="center", va="center", fontsize=7.5,
                color="#374151", family="monospace")

    # Flecha parte_de hacia la consulta
    arr = FancyArrowPatch((x, y), (cx, cy),
                          arrowstyle="-|>", mutation_scale=11,
                          color="#9ca3af", linewidth=1.0,
                          linestyle="dashed")
    ax.add_patch(arr)

# Etiqueta general parte_de
ax.text(11.5, 4.5, "todas parte_de\nconsulta_001",
        ha="center", va="center", fontsize=8.5, style="italic",
        color="#9ca3af", family="monospace")

# Pie
ax.text(7.5, 0.4,
        "La consulta es el nodo articulador; las cinco sub-situaciones son consultables individualmente.\n"
        "Cada una tiene la estructura que su propio contenido semántico exige.",
        ha="center", va="center", fontsize=9.5, style="italic", color="#6b7280")

out = os.path.join(os.path.dirname(__file__), "..", "png",
                   "31_consulta_clinica.png")
plt.savefig(out, dpi=200, bbox_inches="tight", facecolor="#ffffff")
plt.close(fig)
print(f"  ✓ {out}")
