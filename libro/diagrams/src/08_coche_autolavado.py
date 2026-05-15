"""Diagrama: la anécdota del coche y el autolavado.
Comparación lado a lado de:
- Lectura correcta (B): el coche es el paciente (en O)
- Lectura del LLM (A): el coche es un instrumento opcional

Salida: ../png/08_coche_autolavado.png
"""

import os
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

INK = "#1f2937"

fig, ax = plt.subplots(figsize=(13, 8), dpi=200)
ax.set_xlim(0, 13)
ax.set_ylim(0, 8)
ax.axis("off")
fig.patch.set_facecolor("#ffffff")

# Título
ax.text(6.5, 7.65, "El coche y el autolavado: dos lecturas, dos asignaciones de pilares",
        ha="center", va="center", fontsize=14, fontweight="bold", color=INK)

# Pregunta del usuario arriba (común)
quote_box = FancyBboxPatch((1, 6.0), 11, 1.1, boxstyle="round,pad=0.05",
                           facecolor="#f9fafb", edgecolor="#9ca3af", linewidth=1)
ax.add_patch(quote_box)
ax.text(6.5, 6.55,
        '"Estoy en mi coche que se me ensució viniendo del trabajo.\nLo tengo que llevar al autolavado, que me queda a dos cuadras. ¿Me recomiendas ir caminando o en carro?"',
        ha="center", va="center", fontsize=10, style="italic", color=INK)

# Dos columnas para las dos lecturas
LEFT_X = 0.5
RIGHT_X = 6.85
COL_W = 5.65
COL_H = 4.7
COL_Y = 0.8

# Columna izquierda — Lectura B (CORRECTA)
box_left = FancyBboxPatch((LEFT_X, COL_Y), COL_W, COL_H,
                          boxstyle="round,pad=0.08",
                          facecolor="#dcfce7", edgecolor="#15803d", linewidth=1.8)
ax.add_patch(box_left)
ax.text(LEFT_X + COL_W/2, COL_Y + COL_H - 0.4,
        "✓  Lectura correcta",
        ha="center", va="center", fontsize=13, fontweight="bold", color="#065f46")
ax.text(LEFT_X + COL_W/2, COL_Y + COL_H - 0.95,
        "El coche es el paciente del verbo llevar",
        ha="center", va="center", fontsize=10, style="italic", color=INK)

# Tabla de asignación B
rows_B = [
    ("Q", "quién",        "el usuario"),
    ("O", "qué (paciente)", "el coche"),
    ("L", "dónde",        "autolavado, dos cuadras"),
    ("T", "cuándo",       "ahora"),
    ("M", "con_finalidad",   "lavar el coche"),
]
y_row = COL_Y + COL_H - 1.6
for letra, rol, valor in rows_B:
    # Letra circular
    circ = plt.Circle((LEFT_X + 0.5, y_row), 0.20,
                      facecolor="#15803d", edgecolor="white", linewidth=1.2, zorder=3)
    ax.add_patch(circ)
    ax.text(LEFT_X + 0.5, y_row, letra,
            ha="center", va="center", fontsize=11, fontweight="bold", color="white", zorder=4)
    # Rol
    ax.text(LEFT_X + 0.85, y_row, rol,
            ha="left", va="center", fontsize=10, color="#065f46", fontweight="bold")
    # Valor
    ax.text(LEFT_X + 2.6, y_row, "→  " + valor,
            ha="left", va="center", fontsize=10, color=INK)
    y_row -= 0.55

# Recomendación
ax.text(LEFT_X + COL_W/2, COL_Y + 0.35,
        "Conclusión: el coche tiene que ir (es el theme).\nRespuesta: en carro.",
        ha="center", va="center", fontsize=10, color="#065f46", fontweight="bold")

# Columna derecha — Lectura A (LLM)
box_right = FancyBboxPatch((RIGHT_X, COL_Y), COL_W, COL_H,
                           boxstyle="round,pad=0.08",
                           facecolor="#fee2e2", edgecolor="#b91c1c", linewidth=1.8)
ax.add_patch(box_right)
ax.text(RIGHT_X + COL_W/2, COL_Y + COL_H - 0.4,
        "✗  Lectura del LLM",
        ha="center", va="center", fontsize=13, fontweight="bold", color="#7f1d1d")
ax.text(RIGHT_X + COL_W/2, COL_Y + COL_H - 0.95,
        "El coche cae como instrumento opcional",
        ha="center", va="center", fontsize=10, style="italic", color=INK)

# Tabla de asignación A
rows_A = [
    ("Q", "quién",          "el usuario"),
    ("O", "qué (paciente)", "el usuario (¡el mismo!)"),
    ("L", "dónde",          "autolavado, dos cuadras"),
    ("T", "cuándo",         "ahora"),
    ("M", "con_finalidad",  "ir al autolavado"),
]
y_row = COL_Y + COL_H - 1.6
for letra, rol, valor in rows_A:
    circ = plt.Circle((RIGHT_X + 0.5, y_row), 0.20,
                      facecolor="#b91c1c", edgecolor="white", linewidth=1.2, zorder=3)
    ax.add_patch(circ)
    ax.text(RIGHT_X + 0.5, y_row, letra,
            ha="center", va="center", fontsize=11, fontweight="bold", color="white", zorder=4)
    ax.text(RIGHT_X + 0.85, y_row, rol,
            ha="left", va="center", fontsize=10, color="#7f1d1d", fontweight="bold")
    ax.text(RIGHT_X + 2.6, y_row, "→  " + valor,
            ha="left", va="center", fontsize=10, color=INK)
    y_row -= 0.55

ax.text(RIGHT_X + COL_W/2, COL_Y + 0.35,
        "El coche desaparece como paciente.\nSugerencia: ir caminando porque está cerca.",
        ha="center", va="center", fontsize=10, color="#7f1d1d", fontweight="bold")

# Pie
ax.text(6.5, 0.2,
        "El error no fue lógico, fue de modelado del hecho.",
        ha="center", va="center", fontsize=10, style="italic", color="#6b7280")

out = os.path.join(os.path.dirname(__file__), "..", "png",
                   "08_coche_autolavado.png")
plt.savefig(out, dpi=200, bbox_inches="tight", facecolor="#ffffff")
plt.close(fig)
print(f"  ✓ {out}")
