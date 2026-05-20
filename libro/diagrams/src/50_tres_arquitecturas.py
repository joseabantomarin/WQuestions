"""Diagrama: tres arquitecturas para hacer convivir WQuestions con un sistema legacy.
A — vista virtual (sin copia).
B — grafo paralelo (ETL/CDC).
C — híbrido (A + B según el predicado).

Salida: ../png/50_tres_arquitecturas.png
"""

import os
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

INK = "#1f2937"
GRAY = "#6b7280"
SUBTLE = "#9ca3af"

fig, ax = plt.subplots(figsize=(15, 9.5), dpi=200)
ax.set_xlim(0, 15)
ax.set_ylim(0, 9.5)
ax.axis("off")
fig.patch.set_facecolor("#ffffff")

# Título
ax.text(7.5, 9.10,
        "Tres arquitecturas para convivir con un sistema legacy",
        ha="center", va="center", fontsize=14, fontweight="bold", color=INK)
ax.text(7.5, 8.70,
        "Misma capa LLM y misma intención WQuestions arriba; diferente lugar donde viven los datos.",
        ha="center", va="center", fontsize=10, style="italic", color=GRAY)

# ===== Columnas =====
COL_W = 4.4
COL_GAP = 0.4
COL_LEFT_X = [0.5, 0.5 + COL_W + COL_GAP, 0.5 + 2*(COL_W + COL_GAP)]

COL_TITLES = [
    ("A — Vista virtual",       "#1d4ed8"),
    ("B — Grafo paralelo",      "#7c3aed"),
    ("C — Híbrido (recomendado)", "#15803d"),
]
COL_DESC = [
    "Sin copia. El motor traduce\nconsultas a SQL contra el legacy.",
    "Tabla `fact` separada,\nalimentada por ETL desde el legacy.",
    "Legacy para datos transaccionales;\ngrafo aparte para lo semántico-puro.",
]

# Bandas superiores con título
for x, (title, color), desc in zip(COL_LEFT_X, COL_TITLES, COL_DESC):
    header = FancyBboxPatch((x, 7.65), COL_W, 0.85,
                            boxstyle="round,pad=0.06",
                            facecolor=color, edgecolor="none")
    ax.add_patch(header)
    ax.text(x + COL_W/2, 8.20, title, ha="center", va="center",
            fontsize=12, fontweight="bold", color="white")
    ax.text(x + COL_W/2, 7.85, desc, ha="center", va="center",
            fontsize=8.5, color="white", style="italic")


def draw_box(x, y, w, h, label, fill, edge, fontsize=10, style="normal",
             linestyle="-", linewidth=1.4, dashed=False):
    box = FancyBboxPatch((x, y), w, h,
                         boxstyle="round,pad=0.06",
                         facecolor=fill, edgecolor=edge,
                         linewidth=linewidth,
                         linestyle=("--" if dashed else "-"))
    ax.add_patch(box)
    ax.text(x + w/2, y + h/2, label, ha="center", va="center",
            fontsize=fontsize, color=INK, style=style)


def draw_arrow(x1, y1, x2, y2, color=INK, lw=1.2, mut=10):
    arr = FancyArrowPatch((x1, y1), (x2, y2),
                          arrowstyle="-|>", mutation_scale=mut,
                          color=color, linewidth=lw)
    ax.add_patch(arr)


# ===== Capa LLM compartida arriba (informativa) =====
# Estado abstracto: las tres comparten la capa LLM + intención WQuestions
LLM_Y = 6.85
for x in COL_LEFT_X:
    draw_box(x + 0.4, LLM_Y, COL_W - 0.8, 0.55,
             "LLM open-source\n→ intención WQuestions",
             "#fafafa", "#9ca3af", fontsize=8.5, style="italic")
    # Flecha desde LLM hacia el motor (que viene abajo)
    draw_arrow(x + COL_W/2, LLM_Y - 0.02,
               x + COL_W/2, LLM_Y - 0.35,
               color=SUBTLE)


# ===== ARQUITECTURA A — vista virtual =====
xA = COL_LEFT_X[0]
# Motor WQuestions
draw_box(xA + 0.4, 5.65, COL_W - 0.8, 0.55,
         "Motor WQuestions + mapper",
         "#dbeafe", "#1d4ed8", fontsize=9.5)
draw_arrow(xA + COL_W/2, 5.63,
           xA + COL_W/2, 5.30, color="#1d4ed8")
# SQL contra legacy
draw_box(xA + 0.6, 4.65, COL_W - 1.2, 0.55,
         "SQL traducido en vuelo",
         "#fafafa", "#1d4ed8", fontsize=9, style="italic")
draw_arrow(xA + COL_W/2, 4.63,
           xA + COL_W/2, 4.30, color="#1d4ed8")
# MySQL legacy
draw_box(xA + 0.4, 3.50, COL_W - 0.8, 0.70,
         "yaku (MySQL legacy)\nFUENTE ÚNICA DE VERDAD",
         "#fff7ed", "#c2410c", fontsize=9.5)
# Caracteristica
draw_box(xA + 0.3, 2.20, COL_W - 0.6, 0.95,
         "✓ Cero sincronización\n✓ Ve la última venta al instante\n"
         "✗ No modela lo que el legacy no modela",
         "#f9fafb", "#9ca3af", fontsize=8)


# ===== ARQUITECTURA B — grafo paralelo =====
xB = COL_LEFT_X[1]
# Motor
draw_box(xB + 0.4, 5.65, COL_W - 0.8, 0.55,
         "Motor WQuestions",
         "#ede9fe", "#7c3aed", fontsize=9.5)
draw_arrow(xB + COL_W/2, 5.63,
           xB + COL_W/2, 5.30, color="#7c3aed")
# Tabla fact
draw_box(xB + 0.4, 4.55, COL_W - 0.8, 0.70,
         "Tabla fact(subject, predicate,\nobject, t_from, t_to)",
         "#fafafa", "#7c3aed", fontsize=9)
# Flecha desde legacy hacia fact (ETL)
draw_arrow(xB + COL_W/2, 4.20,
           xB + COL_W/2, 4.50, color="#7c3aed", lw=1.4)
ax.text(xB + COL_W/2 + 0.7, 4.35, "ETL /\nCDC",
        ha="left", va="center", fontsize=8, style="italic", color="#7c3aed")
# Legacy
draw_box(xB + 0.4, 3.50, COL_W - 0.8, 0.70,
         "yaku (MySQL legacy)\nlee periódicamente",
         "#fff7ed", "#c2410c", fontsize=9)
# Caracteristica
draw_box(xB + 0.3, 2.20, COL_W - 0.6, 0.95,
         "✓ Modela intenciones, vigencia,\n   modalidades, justificaciones\n"
         "✗ Latencia ETL; doble almacenamiento",
         "#f9fafb", "#9ca3af", fontsize=8)


# ===== ARQUITECTURA C — híbrido =====
xC = COL_LEFT_X[2]
# Motor (con router)
draw_box(xC + 0.4, 5.65, COL_W - 0.8, 0.55,
         "Motor + router por predicado",
         "#dcfce7", "#15803d", fontsize=9.5)
# Dos ramas
draw_arrow(xC + 1.3, 5.63,
           xC + 1.1, 5.10, color="#15803d")
draw_arrow(xC + COL_W - 1.3, 5.63,
           xC + COL_W - 1.1, 5.10, color="#15803d")
# Etiquetas de ramas
ax.text(xC + 0.95, 5.30, "transaccional", ha="center",
        fontsize=7.5, style="italic", color="#15803d")
ax.text(xC + COL_W - 0.95, 5.30, "semántico-puro",
        ha="center", fontsize=7.5, style="italic", color="#15803d")
# Dos backends
draw_box(xC + 0.30, 4.40, (COL_W - 0.7)/2 - 0.1, 0.60,
         "SQL a yaku\n(modo A)",
         "#dbeafe", "#1d4ed8", fontsize=8.5)
draw_box(xC + 0.30 + (COL_W - 0.7)/2 + 0.1, 4.40, (COL_W - 0.7)/2 - 0.1, 0.60,
         "fact paralela\n(modo B)",
         "#ede9fe", "#7c3aed", fontsize=8.5)
# Flecha conjunta hacia legacy
draw_arrow(xC + 1.1, 4.38,
           xC + 1.6, 4.05, color="#1d4ed8", lw=1.1)
draw_arrow(xC + COL_W - 1.1, 4.38,
           xC + COL_W - 1.6, 4.05, color="#7c3aed", lw=1.1)
# Legacy + fact (lado a lado abajo)
draw_box(xC + 0.30, 3.30, (COL_W - 0.7)/2 - 0.1, 0.65,
         "yaku (MySQL)",
         "#fff7ed", "#c2410c", fontsize=9)
draw_box(xC + 0.30 + (COL_W - 0.7)/2 + 0.1, 3.30, (COL_W - 0.7)/2 - 0.1, 0.65,
         "fact (Postgres/MySQL)",
         "#fff7ed", "#c2410c", fontsize=8.5)
# Caracteristica
draw_box(xC + 0.3, 2.20, COL_W - 0.6, 0.95,
         "✓ Lo mejor de ambos mundos\n"
         "✓ Cero riesgo operativo + capa semántica\n"
         "≈ Complejidad de routing",
         "#f9fafb", "#9ca3af", fontsize=8)


# ===== Banda inferior con guía de uso =====
ax.text(7.5, 1.50, "¿Cuándo elegir cada una?",
        ha="center", va="center", fontsize=11, fontweight="bold", color=INK)

choices = [
    (COL_LEFT_X[0] + COL_W/2,
     "POC barato sobre el legacy;\nsolo consultas que el legacy ya modela."),
    (COL_LEFT_X[1] + COL_W/2,
     "Green-field o dominio nuevo;\nbitemporalidad completa requerida."),
    (COL_LEFT_X[2] + COL_W/2,
     "Adoptante real con legacy en producción;\nquiere capacidades semánticas nuevas."),
]
for x, t in choices:
    ax.text(x, 0.85, t, ha="center", va="center",
            fontsize=8.5, color=INK, style="italic")

out = os.path.join(os.path.dirname(__file__), "..", "png", "50_tres_arquitecturas.png")
fig.savefig(out, bbox_inches="tight", facecolor="white", dpi=200)
print(f"Guardado: {out}")
