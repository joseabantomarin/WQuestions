"""Diagrama: cadena causal sin agente en operación minera.

Muestra el caso emblemático del dominio minero: un accidente laboral
cuya cadena causal hacia atrás llega a un evento físico (desprendimiento
de roca) que a su vez es causado por una condición geomecánica
(debilitamiento estructural). En toda la cadena no hay un agente humano
que `hizo` algo — D5 se ejerce a fondo. La situación se modela igual de
limpia que cualquier acción intencional, pero con `causado_por` haciendo
el trabajo en lugar de `agente`.

Salida: ../png/48_minera_cadena_causal.png
"""

import os
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

INK = "#1f2937"

# Colores
ACC_FILL, ACC_EDGE = "#fee2e2", "#b91c1c"     # rojo — el accidente
DES_FILL, DES_EDGE = "#fef3c7", "#b45309"     # ámbar — el desprendimiento
DEB_FILL, DEB_EDGE = "#fed7aa", "#c2410c"     # naranja — el debilitamiento
TURN_FILL, TURN_EDGE = "#dbeafe", "#1d4ed8"   # azul — el turno articulador

fig, ax = plt.subplots(figsize=(14, 9.5), dpi=200)
ax.set_xlim(0, 14)
ax.set_ylim(0, 9.5)
ax.axis("off")
fig.patch.set_facecolor("#ffffff")

# Título
ax.text(7, 9.10,
        "Cadena causal sin agente: un accidente minero rastreado hacia atrás",
        ha="center", va="center", fontsize=14, fontweight="bold", color=INK)
ax.text(7, 8.70,
        "Nadie `hizo` el desprendimiento de roca. Sin embargo el grafo "
        "reconstruye la cadena causal completa: ",
        ha="center", va="center", fontsize=10, style="italic",
        color="#6b7280")
ax.text(7, 8.40,
        "accidente ← desprendimiento ← debilitamiento. D5 admite eventos "
        "sin agente; `causado_por` (D7) hace todo el trabajo.",
        ha="center", va="center", fontsize=10, style="italic",
        color="#6b7280")


def caja(x, y, w, h, title, lines, fill, edge):
    box = FancyBboxPatch((x - w/2, y - h/2), w, h,
                         boxstyle="round,pad=0.05",
                         facecolor=fill, edgecolor=edge,
                         linewidth=1.7)
    ax.add_patch(box)
    ax.text(x, y + h/2 - 0.28, title,
            ha="center", va="center", fontsize=10.5,
            fontweight="bold", color=edge, family="monospace")
    for i, line in enumerate(lines):
        ax.text(x, y + 0.10 - i * 0.22, line,
                ha="center", va="center", fontsize=8,
                color="#374151")


# ─────────────────────────────────────────────────────────────
# Tres cajas alineadas horizontalmente
# ─────────────────────────────────────────────────────────────

# Izquierda — el accidente
caja(2.5, 5.2, 3.4, 1.8, "accidente_001",
     ["tipo: accidente laboral",
      "paciente: op. Quispe",
      "lugar: Frente A",
      "momento: 19-May 11:40",
      "tipo_lesion: contusión"],
     ACC_FILL, ACC_EDGE)

# Centro — el desprendimiento (sin agente)
caja(7.0, 5.2, 3.4, 1.8, "desprendimiento_001",
     ["evento_geomecánico",
      "lugar: Frente A",
      "momento: 19-May 11:40",
      "★ SIN AGENTE ★",
      "(nadie lo \"hizo\")"],
     DES_FILL, DES_EDGE)

# Derecha — el debilitamiento previo
caja(11.5, 5.2, 3.0, 1.8, "debilitamiento",
     ["condición_geomecánica",
      "pared Banco 03",
      "(condición previa)",
      "★ SIN AGENTE ★"],
     DEB_FILL, DEB_EDGE)

# Flecha 1: accidente ← desprendimiento
arr1 = FancyArrowPatch((5.3, 5.2), (4.2, 5.2),
                       arrowstyle="-|>", mutation_scale=14,
                       color=ACC_EDGE, linewidth=1.6)
ax.add_patch(arr1)
ax.text(4.75, 5.55, "causado_por",
        ha="center", va="center", fontsize=9, fontweight="bold",
        color=ACC_EDGE, family="monospace",
        bbox=dict(boxstyle="round,pad=0.18",
                  facecolor="white", edgecolor="none", alpha=0.95))

# Flecha 2: desprendimiento ← debilitamiento
arr2 = FancyArrowPatch((10.0, 5.2), (8.7, 5.2),
                       arrowstyle="-|>", mutation_scale=14,
                       color=DES_EDGE, linewidth=1.6)
ax.add_patch(arr2)
ax.text(9.35, 5.55, "causado_por",
        ha="center", va="center", fontsize=9, fontweight="bold",
        color=DES_EDGE, family="monospace",
        bbox=dict(boxstyle="round,pad=0.18",
                  facecolor="white", edgecolor="none", alpha=0.95))

# ─────────────────────────────────────────────────────────────
# Arriba — el turno articulador que contiene todo
# ─────────────────────────────────────────────────────────────
caja(7.0, 7.3, 5.5, 1.0, "turno_dia_2026_05_19",
     ["turno minero · 3 operadores · supervisor Huamán",
      "06:00 → 18:00 · Tajo Norte"],
     TURN_FILL, TURN_EDGE)

# Flecha del accidente al turno (parte_de)
arr_pte = FancyArrowPatch((2.5, 6.1), (5.5, 6.8),
                          arrowstyle="-|>", mutation_scale=12,
                          color=TURN_EDGE, linewidth=1.4,
                          connectionstyle="arc3,rad=-0.25")
ax.add_patch(arr_pte)
ax.text(3.5, 7.0, "parte_de",
        ha="center", va="center", fontsize=8.5, fontweight="bold",
        color=TURN_EDGE, family="monospace",
        bbox=dict(boxstyle="round,pad=0.15",
                  facecolor="white", edgecolor="none", alpha=0.92))

# ─────────────────────────────────────────────────────────────
# Abajo — comparativa con un evento típico CON agente
# ─────────────────────────────────────────────────────────────
ax.text(7, 3.4,
        "Comparativa — el modelo trata ambos casos con la misma forma:",
        ha="center", va="center", fontsize=10.5, fontweight="bold",
        color=INK)

# Caja con agente
caja(3.5, 2.0, 5.0, 1.8,
     "extracción CON agente",
     ["agente: op. Quispe       ← presente",
      "tema: mineral_oro",
      "monto: 2400 toneladas",
      "lugar_de: Frente A"],
     "#dcfce7", "#15803d")

# Caja sin agente
caja(10.5, 2.0, 5.0, 1.8,
     "desprendimiento SIN agente",
     ["(agente AUSENTE)         ← D5 lo admite",
      "causado_por: debilitamiento",
      "lugar_de: Frente A",
      "momento: 11:40"],
     "#fef3c7", "#b45309")

# Pie
ax.text(7, 0.45,
        "Cualquier auditor de seguridad puede recorrer la cadena causal hacia atrás "
        "y producir el informe completo sin gimnasia.",
        ha="center", va="center", fontsize=9.5, color="#374151",
        style="italic")

out = os.path.join(os.path.dirname(__file__), "..", "png",
                   "48_minera_cadena_causal.png")
plt.savefig(out, dpi=200, bbox_inches="tight", facecolor="#ffffff")
plt.close(fig)
print(f"  ✓ {out}")
