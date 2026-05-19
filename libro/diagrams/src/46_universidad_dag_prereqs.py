"""Diagrama: DAG de prerequisitos académicos.

Muestra cómo los cursos universitarios se conectan a través del rol
`requiere_prerequisito` formando un grafo dirigido acíclico (DAG).
Cada curso es un O en el grafo; las flechas son la dependencia académica.
La inscripción a un curso es válida solo si los prerequisitos están aprobados.

Salida: ../png/46_universidad_dag_prereqs.png
"""

import os
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

INK = "#1f2937"

# Colores por semestre
COLORS = {
    "sem1_fill": "#dbeafe", "sem1_edge": "#1d4ed8",  # azul — primer semestre
    "sem2_fill": "#fef3c7", "sem2_edge": "#b45309",  # ámbar — segundo
    "sem3_fill": "#fee2e2", "sem3_edge": "#b91c1c",  # rojo — tercero (avanzados)
}

cursos = {
    # Primer semestre
    "Mate I":           (2.0, 6.5, "sem1_fill", "sem1_edge"),
    "Intro Prog":       (5.5, 6.5, "sem1_fill", "sem1_edge"),
    "Física I":         (9.0, 6.5, "sem1_fill", "sem1_edge"),
    # Segundo semestre
    "Mate II":          (2.0, 4.0, "sem2_fill", "sem2_edge"),
    "Estructuras Datos":(5.5, 4.0, "sem2_fill", "sem2_edge"),
    "Física II":        (9.0, 4.0, "sem2_fill", "sem2_edge"),
    # Tercer semestre (avanzados con doble prerequisito)
    "Algoritmos Av.":   (3.7, 1.5, "sem3_fill", "sem3_edge"),
    "Cálculo Vec.":     (9.0, 1.5, "sem3_fill", "sem3_edge"),
}

prereqs = [
    ("Mate II",            "Mate I"),
    ("Estructuras Datos",  "Intro Prog"),
    ("Física II",          "Física I"),
    # Algoritmos requiere DOS prerequisitos (de distinto semestre)
    ("Algoritmos Av.",     "Mate II"),
    ("Algoritmos Av.",     "Estructuras Datos"),
    ("Cálculo Vec.",       "Mate II"),
    ("Cálculo Vec.",       "Física II"),
]

fig, ax = plt.subplots(figsize=(13, 9), dpi=200)
ax.set_xlim(0, 12)
ax.set_ylim(0, 9)
ax.axis("off")
fig.patch.set_facecolor("#ffffff")

# Título
ax.text(6, 8.55,
        "DAG de prerequisitos: la malla curricular como grafo",
        ha="center", va="center", fontsize=14, fontweight="bold", color=INK)
ax.text(6, 8.15,
        "Cada curso es un individuo en O; cada arista es una tripleta "
        "(curso, requiere_prerequisito, otro_curso).",
        ha="center", va="center", fontsize=10, style="italic",
        color="#6b7280")
ax.text(6, 7.85,
        "La inscripción a un curso solo es válida si todos sus prerequisitos están aprobados.",
        ha="center", va="center", fontsize=10, style="italic",
        color="#6b7280")

# Etiquetas de semestre a la izquierda
ax.text(0.4, 6.5, "Semestre I",
        ha="center", va="center", fontsize=10, fontweight="bold",
        color=COLORS["sem1_edge"], rotation=90)
ax.text(0.4, 4.0, "Semestre II",
        ha="center", va="center", fontsize=10, fontweight="bold",
        color=COLORS["sem2_edge"], rotation=90)
ax.text(0.4, 1.5, "Semestre III",
        ha="center", va="center", fontsize=10, fontweight="bold",
        color=COLORS["sem3_edge"], rotation=90)

# Líneas horizontales tenues separando semestres
for y in [5.25, 2.75]:
    ax.plot([1.0, 11.0], [y, y], color="#e5e7eb",
            linewidth=1, linestyle="--", zorder=0)

# Cajas de cursos
box_w, box_h = 2.4, 0.9
node_positions = {}
for nombre, (x, y, fill, edge) in cursos.items():
    box = FancyBboxPatch((x - box_w/2, y - box_h/2), box_w, box_h,
                         boxstyle="round,pad=0.05",
                         facecolor=COLORS[fill],
                         edgecolor=COLORS[edge],
                         linewidth=1.5)
    ax.add_patch(box)
    ax.text(x, y, nombre,
            ha="center", va="center", fontsize=10, fontweight="bold",
            color=COLORS[edge])
    node_positions[nombre] = (x, y)

# Flechas de prerequisitos
for hijo, prereq in prereqs:
    x1, y1 = node_positions[prereq]
    x2, y2 = node_positions[hijo]
    arr = FancyArrowPatch((x1, y1 - box_h/2),
                          (x2, y2 + box_h/2),
                          arrowstyle="-|>", mutation_scale=12,
                          color="#6b7280", linewidth=1.2,
                          connectionstyle="arc3,rad=0.0")
    ax.add_patch(arr)

# Leyenda
ax.text(11.5, 6.5, "→",
        ha="center", va="center", fontsize=14, color="#6b7280")
ax.text(11.5, 6.15, "requiere",
        ha="center", va="center", fontsize=8.5, color="#6b7280",
        family="monospace")
ax.text(11.5, 5.95, "prerequisito",
        ha="center", va="center", fontsize=8.5, color="#6b7280",
        family="monospace")

# Pie
ax.text(6, 0.45,
        "Algoritmos Avanzados requiere DOS prerequisitos simultáneos. "
        "La consulta `quiero inscribirme a Algoritmos`",
        ha="center", va="center", fontsize=9.5, color="#374151",
        style="italic")
ax.text(6, 0.18,
        "verifica que el grafo de aprobados del estudiante contenga ambos. "
        "Es un recorrido — no un join.",
        ha="center", va="center", fontsize=9.5, color="#374151",
        style="italic")

out = os.path.join(os.path.dirname(__file__), "..", "png",
                   "46_universidad_dag_prereqs.png")
plt.savefig(out, dpi=200, bbox_inches="tight", facecolor="#ffffff")
plt.close(fig)
print(f"  ✓ {out}")
