"""Diagrama: cadena explicativa.
Una secuencia de situaciones encadenadas por relaciones del 'por qué',
con tipos distintos (causalidad, motivación) etiquetados.

Caso: renuncia del ministro como nodo final, hacia atrás:
investigación ← publicación ← filtración ← disconformidad.

Salida: ../png/20_cadena_explicativa.png
"""

import os
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

INK = "#1f2937"
O_FILL, O_EDGE = "#dcfce7", "#15803d"
CAUSA_EDGE = "#b91c1c"
MOTIVO_EDGE = "#b45309"

fig, ax = plt.subplots(figsize=(14, 7), dpi=200)
ax.set_xlim(0, 14)
ax.set_ylim(0, 7)
ax.axis("off")
fig.patch.set_facecolor("#ffffff")

# Título
ax.text(7, 6.6, "Cadena explicativa: cómo las relaciones del \"por qué\" reconstruyen una historia",
        ha="center", va="center", fontsize=14, fontweight="bold", color=INK)
ax.text(7, 6.2,
        "Cuatro situaciones conectadas: dos motivos psicológicos y dos causas físicas, distinguidos en el grafo.",
        ha="center", va="center", fontsize=10, style="italic", color="#6b7280")

# Cinco situaciones en línea horizontal (de derecha a izquierda en la narrativa)
# Pero las dibujamos de izquierda a derecha en orden cronológico, y las flechas
# del 'por qué' apuntan del posterior al previo (retrospectivas).
situations = [
    (1.6,  "disconformidad_\nfuncionario_001",  "estado mental"),
    (4.4,  "filtracion_001",                     "acción"),
    (7.0,  "publicacion_nota_001",               "acción mediática"),
    (9.6,  "investigacion_001",                  "proceso institucional"),
    (12.4, "renuncia_ministro_001",              "decisión final"),
]

y_band = 3.5

for x, label, sub in situations:
    box = FancyBboxPatch((x - 1.05, y_band - 0.5), 2.1, 1.0,
                         boxstyle="round,pad=0.05",
                         facecolor=O_FILL, edgecolor=O_EDGE, linewidth=1.8)
    ax.add_patch(box)
    ax.text(x, y_band + 0.18, label, ha="center", va="center",
            fontsize=9, fontweight="bold", color=O_EDGE, family="monospace")
    ax.text(x, y_band - 0.27, sub, ha="center", va="center",
            fontsize=8, style="italic", color="#6b7280")

# Relaciones (flechas hacia atrás: del consecuente al antecedente)
# situations: 0 disconformidad, 1 filtracion, 2 publicacion, 3 investigacion, 4 renuncia
edges = [
    # (origen_idx, destino_idx, relacion, color)
    (1, 0, "motivado_por",  MOTIVO_EDGE),
    (2, 1, "causado_por",   CAUSA_EDGE),
    (3, 2, "causado_por",   CAUSA_EDGE),
    (4, 3, "motivado_por",  MOTIVO_EDGE),
]

for src_i, dst_i, rel, color in edges:
    xs = situations[src_i][0]
    xd = situations[dst_i][0]
    # Curva por encima para que la flecha "retrospectiva" no se cruce con la caja
    arr = FancyArrowPatch((xs - 1.05, y_band + 0.2),
                          (xd + 1.05, y_band + 0.2),
                          arrowstyle="-|>", mutation_scale=15,
                          color=color, linewidth=1.6,
                          connectionstyle="arc3,rad=0.45")
    ax.add_patch(arr)
    # Etiqueta sobre la curva
    mid_x = (xs + xd) / 2
    ax.text(mid_x, y_band + 1.40, rel, ha="center", va="center",
            fontsize=9, fontweight="bold", color=color,
            family="monospace",
            bbox=dict(boxstyle="round,pad=0.18", facecolor="white",
                      edgecolor=color, alpha=0.95, linewidth=0.8))

# Eje temporal subtle abajo
ax.annotate("", xy=(13.2, 1.7), xytext=(0.8, 1.7),
            arrowprops=dict(arrowstyle="->", color="#9ca3af", lw=1.0))
ax.text(0.8, 1.45, "antes", ha="left", va="center",
        fontsize=8.5, style="italic", color="#6b7280")
ax.text(13.2, 1.45, "después", ha="right", va="center",
        fontsize=8.5, style="italic", color="#6b7280")
ax.text(7, 1.42, "tiempo cronológico",
        ha="center", va="center", fontsize=8, style="italic", color="#9ca3af")

# Leyenda — colores
leg_y = 0.6
ax.text(1.0, leg_y, "● causado_por", ha="left", va="center",
        fontsize=9, color=CAUSA_EDGE, fontweight="bold")
ax.text(1.0, leg_y - 0.30, "causalidad mecánica entre eventos",
        ha="left", va="center", fontsize=8.5, style="italic", color="#6b7280")

ax.text(7.5, leg_y, "● motivado_por", ha="left", va="center",
        fontsize=9, color=MOTIVO_EDGE, fontweight="bold")
ax.text(7.5, leg_y - 0.30, "motivación intencional de un agente",
        ha="left", va="center", fontsize=8.5, style="italic", color="#6b7280")

out = os.path.join(os.path.dirname(__file__), "..", "png",
                   "20_cadena_explicativa.png")
plt.savefig(out, dpi=200, bbox_inches="tight", facecolor="#ffffff")
plt.close(fig)
print(f"  ✓ {out}")
