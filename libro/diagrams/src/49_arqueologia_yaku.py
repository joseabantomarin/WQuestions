"""Diagrama: arqueología semántica de yaku.
Mapea las tablas existentes del MySQL legacy a los 8 ejes WQuestions.
Rectángulos sólidos = lo que yaku ya implementa (informalmente).
Rectángulos punteados = lo que falta y WQuestions añadiría.

Salida: ../png/49_arqueologia_yaku.png
"""

import os
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

INK = "#1f2937"
GRAY = "#6b7280"

fig, ax = plt.subplots(figsize=(15, 9.5), dpi=200)
ax.set_xlim(0, 15)
ax.set_ylim(0, 9.5)
ax.axis("off")
fig.patch.set_facecolor("#ffffff")

# Título
ax.text(7.5, 9.10, "Arqueología semántica: las tablas de yaku proyectadas a los 8 ejes",
        ha="center", va="center", fontsize=14, fontweight="bold", color=INK)
ax.text(7.5, 8.70,
        "Cajas sólidas = ya implementado en yaku (informalmente). Cajas punteadas = lo que WQuestions añade.",
        ha="center", va="center", fontsize=10, style="italic", color=GRAY)

# ---- LADO IZQUIERDO: tablas yaku ----
ax.text(2.0, 8.10, "Tablas yaku (MySQL)",
        ha="center", va="center", fontsize=11, fontweight="bold", color=INK)

YAKU_TABLES = [
    ("cliente",            "#fef3c7", "#b45309"),
    ("persona",            "#fef3c7", "#b45309"),
    ("producto",           "#dcfce7", "#15803d"),
    ("venta",              "#dcfce7", "#15803d"),
    ("ventadet",           "#dcfce7", "#15803d"),
    ("asistencia",         "#dcfce7", "#15803d"),
    ("socio",              "#dcfce7", "#15803d"),
    ("plan",               "#e0e7ff", "#4f46e5"),
    ("compra/compdet",     "#dcfce7", "#15803d"),
]

t_y_start = 7.50
t_y_step = 0.62
for i, (name, fill, edge) in enumerate(YAKU_TABLES):
    y = t_y_start - i * t_y_step
    box = FancyBboxPatch((0.4, y - 0.22), 3.2, 0.44,
                         boxstyle="round,pad=0.04",
                         facecolor=fill, edgecolor=edge, linewidth=1.4)
    ax.add_patch(box)
    ax.text(2.0, y, name, ha="center", va="center",
            fontsize=10, color=INK, family="monospace")

# ---- LADO DERECHO: 8 ejes WQuestions ----
ax.text(12.5, 8.10, "Ejes WQuestions",
        ha="center", va="center", fontsize=11, fontweight="bold", color=INK)

AXES = [
    ("Q", "quién",  "#dbeafe", "#1d4ed8"),
    ("O", "qué",    "#dcfce7", "#15803d"),
    ("L", "dónde",  "#fef3c7", "#b45309"),
    ("T", "cuándo", "#fed7aa", "#c2410c"),
    ("N", "cuánto", "#e9d5ff", "#7c3aed"),
    ("K", "clase",  "#e0e7ff", "#4f46e5"),
    ("P", "cuál",   "#fce7f3", "#be185d"),
    ("M", "cómo",   "#cffafe", "#0e7490"),
]

# Tres categorías visuales: sólido (ya está), punteado (falta), mixto
# Para cada eje, indicamos qué tablas yaku contribuyen y qué falta
EJE_ESTADO = {
    "Q": ("solido", "cliente, persona"),
    "O": ("solido", "venta, ventadet, asistencia, socio"),
    "L": ("punteado", "habitaciones son productos (cap.15 dualidad)"),
    "T": ("solido", "fechas, horas, vigencias en socio.desde/hasta (D6 ✓)"),
    "N": ("solido", "IMPORTE, PRECIO, CANTIDAD, STOCK"),
    "K": ("mixto", "producto.MARCA implícita; planes sin tipar"),
    "P": ("solido", "atributos no-clave"),
    "M": ("punteado", "cubierto_por, durante, justificado_por faltan"),
}

e_y_start = 7.50
e_y_step = 0.78
for i, (code, name, fill, edge) in enumerate(AXES):
    y = e_y_start - i * e_y_step
    estado, _detalle = EJE_ESTADO[code]
    is_punteado = (estado == "punteado")
    is_mixto = (estado == "mixto")

    linestyle = "--" if is_punteado else "-"
    lw = 1.4 if not is_punteado else 1.8

    box = FancyBboxPatch((10.4, y - 0.28), 4.2, 0.56,
                         boxstyle="round,pad=0.04",
                         facecolor=fill, edgecolor=edge,
                         linewidth=lw, linestyle=linestyle)
    ax.add_patch(box)
    # Chip con código
    chip = FancyBboxPatch((10.55, y - 0.18), 0.40, 0.40,
                          boxstyle="round,pad=0.02",
                          facecolor=edge, edgecolor="none")
    ax.add_patch(chip)
    ax.text(10.75, y + 0.025, code, ha="center", va="center",
            fontsize=11, color="white", fontweight="bold", family="monospace")
    ax.text(11.15, y + 0.10, name, ha="left", va="center",
            fontsize=10.5, fontweight="bold", color=edge)

    # Estado (texto pequeño dentro de la caja)
    if is_mixto:
        estado_lbl = "parcial"
    elif is_punteado:
        estado_lbl = "falta — WQuestions añade"
    else:
        estado_lbl = "ya en yaku"
    ax.text(11.15, y - 0.12, estado_lbl, ha="left", va="center",
            fontsize=8, style="italic", color=GRAY)

# ---- CONEXIONES (líneas que mapean tabla → eje) ----
# Coordenadas: tablas en x=3.6 (lado derecho), ejes en x=10.4 (lado izquierdo)
def y_of_table(name):
    for i, (n, _, _) in enumerate(YAKU_TABLES):
        if n == name:
            return t_y_start - i * t_y_step
    return None

def y_of_eje(code):
    for i, (c, _, _, _) in enumerate(AXES):
        if c == code:
            return e_y_start - i * e_y_step
    return None

# Mapeos (tabla → eje). Tono según relevancia.
CONNECTIONS = [
    ("cliente",        "Q"),
    ("persona",        "Q"),
    ("producto",       "K"),
    ("producto",       "O"),
    ("venta",          "O"),
    ("venta",          "T"),
    ("venta",          "N"),
    ("ventadet",       "O"),
    ("ventadet",       "N"),
    ("asistencia",     "O"),
    ("asistencia",     "T"),
    ("socio",          "T"),
    ("socio",          "O"),
    ("plan",           "K"),
    ("compra/compdet", "O"),
]

for src, dst in CONNECTIONS:
    y_s = y_of_table(src)
    y_d = y_of_eje(dst)
    if y_s is None or y_d is None:
        continue
    arrow = FancyArrowPatch((3.65, y_s), (10.35, y_d),
                            arrowstyle="-|>", mutation_scale=8,
                            color="#9ca3af", linewidth=0.9, alpha=0.75)
    ax.add_patch(arrow)

# ---- Anotaciones destacadas ----
# Cajas en el centro con los tres hallazgos clave
ANOTACIONES = [
    (5.0, 5.4, 9.0, 5.4,
     "socio.desde / socio.hasta\n≡ regla D6 (vigencia temporal)",
     "#15803d"),
    (5.0, 3.6, 9.0, 3.6,
     "venta.ANULA / CANCELADO\n≡ embrión de estatus_factual",
     "#15803d"),
    (5.0, 1.8, 9.0, 1.8,
     "producto.MARCA codifica eje K\n(disfrazado de 'marca comercial')",
     "#4f46e5"),
]
for x1, y1, x2, y2, txt, color in ANOTACIONES:
    box = FancyBboxPatch((x1 - 1.7, y1 - 0.55), 3.4, 1.10,
                         boxstyle="round,pad=0.06",
                         facecolor="#fafafa", edgecolor=color,
                         linewidth=1.3)
    ax.add_patch(box)
    ax.text(x1, y1, txt, ha="center", va="center", fontsize=9, color=INK)

# Etiqueta inferior — gaps
ax.text(7.5, 0.55,
        "Lo que falta (cajas punteadas): vigencia histórica de propiedades del cliente, "
        "modalidades de cobertura, justificaciones formales.",
        ha="center", va="center", fontsize=9, style="italic", color="#7c2d12")

out = os.path.join(os.path.dirname(__file__), "..", "png", "49_arqueologia_yaku.png")
fig.savefig(out, bbox_inches="tight", facecolor="white", dpi=200)
print(f"Guardado: {out}")
