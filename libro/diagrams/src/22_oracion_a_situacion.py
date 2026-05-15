"""Diagrama: de oración del español a situación reificada.
Muestra cómo cada constituyente sintáctico se mapea a un rol canónico,
produciendo hechos atómicos sobre una situación reificada. La cláusula
final genera una sub-situación.

Salida: ../png/22_oracion_a_situacion.png
"""

import os
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

INK = "#1f2937"
TYPE_COLORS = {
    "Q": "#1d4ed8",
    "O": "#15803d",
    "L": "#b45309",
    "T": "#c2410c",
    "K": "#4f46e5",
}

fig, ax = plt.subplots(figsize=(15, 10), dpi=200)
ax.set_xlim(0, 15)
ax.set_ylim(0, 10)
ax.axis("off")
fig.patch.set_facecolor("#ffffff")

# Título
ax.text(7.5, 9.55, "De oración a situación reificada",
        ha="center", va="center", fontsize=14, fontweight="bold", color=INK)
ax.text(7.5, 9.15,
        "Cada constituyente sintáctico de la oración se convierte en un hecho atómico sobre la situación.",
        ha="center", va="center", fontsize=10, style="italic", color="#6b7280")

# ----- Fila 1: la oración -----
sentence_y = 8.2
segments = [
    ("Juan",                  1.3,  "agente",        "Q"),
    ("le dio",                2.4,  None,            None),
    ("un libro",              3.8,  "tema",          "O"),
    ("a María",               5.4,  "beneficiario",  "Q"),
    ("ayer",                  7.0,  "momento",       "T"),
    ("en su casa",            8.5,  "lugar_de",      "L"),
    ("para sorprenderla",     10.7, "con_finalidad", "O"),
]

ax.add_patch(FancyBboxPatch((0.6, sentence_y - 0.45), 12.2, 0.9,
                            boxstyle="round,pad=0.05",
                            facecolor="#f9fafb", edgecolor="#9ca3af",
                            linewidth=1.0))

for txt, cx, role, eje in segments:
    if eje is None:
        ax.text(cx, sentence_y, txt, ha="center", va="center",
                fontsize=11, fontweight="bold", color="#15803d",
                family="serif", style="italic")
    else:
        color = TYPE_COLORS[eje]
        ax.text(cx, sentence_y, txt, ha="center", va="center",
                fontsize=11, color=color, family="serif")
        ax.text(cx, sentence_y - 0.65, f"→ {role}",
                ha="center", va="center", fontsize=8.5,
                color=color, style="italic", family="monospace")

ax.text(13.7, sentence_y, "verbo: dar →",
        ha="left", va="center", fontsize=10,
        style="italic", color="#15803d", family="monospace")

# ----- Fila 2: la situación reificada -----
situ_y = 5.5
situ_box = FancyBboxPatch((5.5, situ_y - 0.55), 4.0, 1.10,
                          boxstyle="round,pad=0.06",
                          facecolor="#dcfce7", edgecolor="#15803d",
                          linewidth=2.5)
ax.add_patch(situ_box)
ax.text(7.5, situ_y + 0.20, "dar_001",
        ha="center", va="center", fontsize=13, fontweight="bold",
        color="#15803d", family="monospace")
ax.text(7.5, situ_y - 0.20, "∈ O   (situación reificada)",
        ha="center", va="center", fontsize=9, style="italic", color="#6b7280")

# Etiqueta entre filas 1 y 2: "se reifica"
ax.annotate("", xy=(7.5, situ_y + 0.55), xytext=(7.5, sentence_y - 0.95),
            arrowprops=dict(arrowstyle="->", color="#9ca3af",
                            lw=1.0, linestyle="dashed"))
ax.text(7.95, (sentence_y + situ_y) / 2, "se reifica",
        ha="left", va="center", fontsize=9, style="italic",
        color="#6b7280")

# ----- Fila 3: hechos atómicos -----
facts = [
    ("instancia_de",   "accion_dar",    "K", 1.3),
    ("agente",         "juan",          "Q", 3.5),
    ("tema",           "libro_007",     "O", 5.7),
    ("beneficiario",   "maria",         "Q", 7.9),
    ("momento",        "2026-05-12",    "T", 10.1),
    ("lugar_de",       "casa_juan",     "L", 12.3),
]
fact_y = 3.5

for role, val, eje, fx in facts:
    color = TYPE_COLORS.get(eje, "#4f46e5")
    box = FancyBboxPatch((fx - 1.0, fact_y - 0.42), 2.0, 0.88,
                         boxstyle="round,pad=0.04",
                         facecolor="#f9fafb", edgecolor=color, linewidth=1.3)
    ax.add_patch(box)
    ax.text(fx, fact_y + 0.20, role,
            ha="center", va="center", fontsize=8.8,
            color=color, fontweight="bold", family="monospace")
    ax.text(fx, fact_y - 0.10, val,
            ha="center", va="center", fontsize=9,
            color="#374151", family="monospace")
    ax.text(fx + 0.78, fact_y - 0.30, f"∈ {eje}",
            ha="right", va="center", fontsize=7, style="italic",
            color="#6b7280")
    # Flecha desde la situación
    arr = FancyArrowPatch((7.5, situ_y - 0.6), (fx, fact_y + 0.46),
                          arrowstyle="-|>", mutation_scale=10,
                          color="#9ca3af", linewidth=0.8,
                          connectionstyle="arc3,rad=0.0")
    ax.add_patch(arr)

# ----- Fila 4: con_finalidad → sub-situación -----
# Un séptimo hecho atómico centrado debajo, con la sub-situación expandida
cf_y = 1.6
cf_x = 7.5
cf_box = FancyBboxPatch((cf_x - 1.7, cf_y - 0.42), 3.4, 0.88,
                        boxstyle="round,pad=0.04",
                        facecolor="#f9fafb", edgecolor="#15803d", linewidth=1.5)
ax.add_patch(cf_box)
ax.text(cf_x, cf_y + 0.20, "con_finalidad",
        ha="center", va="center", fontsize=9,
        color="#15803d", fontweight="bold", family="monospace")
ax.text(cf_x, cf_y - 0.10, "sorprender_001",
        ha="center", va="center", fontsize=9.5,
        color="#374151", family="monospace", fontweight="bold")
ax.text(cf_x + 1.55, cf_y - 0.30, "∈ O",
        ha="right", va="center", fontsize=7, style="italic",
        color="#6b7280")

# Flecha desde la situación hacia este hecho
arr = FancyArrowPatch((7.5, situ_y - 0.6), (cf_x, cf_y + 0.46),
                      arrowstyle="-|>", mutation_scale=10,
                      color="#15803d", linewidth=1.0,
                      connectionstyle="arc3,rad=0.0")
ax.add_patch(arr)

# Sub-situación expandida (al lado derecho del rol con_finalidad)
sub_y = 1.6
sub_cx = 12.3
sub_w = 4.4
sub_box = FancyBboxPatch((sub_cx - sub_w/2, sub_y - 0.42), sub_w, 0.88,
                         boxstyle="round,pad=0.05",
                         facecolor="#dcfce7", edgecolor="#15803d",
                         linewidth=1.5)
ax.add_patch(sub_box)
ax.text(sub_cx, sub_y + 0.20, "sorprender_001",
        ha="center", va="center", fontsize=10, fontweight="bold",
        color="#15803d", family="monospace")
ax.text(sub_cx, sub_y - 0.18, "agente: juan · paciente: maria",
        ha="center", va="center", fontsize=8, color="#374151",
        family="monospace")
# Flecha horizontal del valor a la sub-situación expandida
arr = FancyArrowPatch((cf_x + 1.7, sub_y), (sub_cx - sub_w/2, sub_y),
                      arrowstyle="-|>", mutation_scale=12,
                      color="#15803d", linewidth=1.2, linestyle="dashed")
ax.add_patch(arr)
ax.text((cf_x + 1.7 + sub_cx - sub_w/2) / 2, sub_y + 0.30,
        "expande →",
        ha="center", va="center", fontsize=8.5,
        style="italic", color="#15803d", family="monospace")

# Pie
ax.text(7.5, 0.30,
        "Una oración → 6 hechos atómicos + 1 sub-situación. Procedimiento mecánico, idéntico para cualquier dominio.",
        ha="center", va="center", fontsize=9.5, style="italic", color="#6b7280")

out = os.path.join(os.path.dirname(__file__), "..", "png",
                   "22_oracion_a_situacion.png")
plt.savefig(out, dpi=200, bbox_inches="tight", facecolor="#ffffff")
plt.close(fig)
print(f"  ✓ {out}")
