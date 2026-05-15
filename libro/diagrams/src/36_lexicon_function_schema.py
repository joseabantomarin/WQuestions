"""Diagrama: entrada del lexicon ≡ function schema.

Dos columnas paralelas mostrando la correspondencia uno-a-uno entre
una entrada del lexicon (forma interna) y un schema JSON expuesto
a un LLM vía function calling / MCP.

Salida: ../png/36_lexicon_function_schema.png
"""

import os
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

INK = "#1f2937"
LEX_FILL, LEX_EDGE = "#dbeafe", "#1d4ed8"
FN_FILL, FN_EDGE = "#e0e7ff", "#4f46e5"

fig, ax = plt.subplots(figsize=(15, 9), dpi=200)
ax.set_xlim(0, 15)
ax.set_ylim(0, 9)
ax.axis("off")
fig.patch.set_facecolor("#ffffff")

# Título
ax.text(7.5, 8.55,
        "Una entrada del lexicon ES un function schema",
        ha="center", va="center", fontsize=14, fontweight="bold", color=INK)
ax.text(7.5, 8.15,
        "Correspondencia directa, sin adaptador: cada verbo del lexicon es invocable por un LLM.",
        ha="center", va="center", fontsize=10, style="italic", color="#6b7280")

# ---- Columna izquierda: Lexicon entry ----
left_x = 0.7
col_w = 6.5
top_y = 7.3
bot_y = 1.2

box_l = FancyBboxPatch((left_x, bot_y), col_w, top_y - bot_y,
                      boxstyle="round,pad=0.05",
                      facecolor=LEX_FILL, edgecolor=LEX_EDGE, linewidth=1.8)
ax.add_patch(box_l)
ax.text(left_x + col_w/2, top_y - 0.3, "LEXICON ENTRY (interno)",
        ha="center", va="center", fontsize=12, fontweight="bold",
        color=LEX_EDGE)
ax.text(left_x + col_w/2, top_y - 0.6, "(forma YAML usada por el modelo)",
        ha="center", va="center", fontsize=8.5, style="italic", color="#1e3a8a")

lex_lines = [
    "verb: prescribir",
    "  situation_type: accion_prescribir",
    "  obligatory:",
    "    [agente, paciente,",
    "     medicamento_prescrito]",
    "  optional:",
    "    [frecuencia, duracion, momento]",
    "  aliases:",
    "    agente: [\"doctor\", \"médico\"]",
    "    paciente: [\"paciente\"]",
    "    medicamento_prescrito:",
    "      [\"fármaco\", \"medicación\"]",
    "  signature:",
    "    agente:                Q",
    "    paciente:              Q",
    "    medicamento_prescrito: K",
    "    frecuencia:            K",
    "    momento:               T",
]
for i, line in enumerate(lex_lines):
    ax.text(left_x + 0.25, top_y - 1.1 - i * 0.28, line,
            ha="left", va="center", fontsize=8.5,
            color=INK, family="monospace")

# ---- Columna derecha: Function schema (MCP) ----
right_x = 8.0
box_r = FancyBboxPatch((right_x, bot_y), col_w, top_y - bot_y,
                      boxstyle="round,pad=0.05",
                      facecolor=FN_FILL, edgecolor=FN_EDGE, linewidth=1.8)
ax.add_patch(box_r)
ax.text(right_x + col_w/2, top_y - 0.3, "FUNCTION SCHEMA (expuesto)",
        ha="center", va="center", fontsize=12, fontweight="bold",
        color=FN_EDGE)
ax.text(right_x + col_w/2, top_y - 0.6, "(JSON consumido por LLM / MCP)",
        ha="center", va="center", fontsize=8.5, style="italic", color="#3730a3")

fn_lines = [
    "{",
    "  \"name\": \"prescribir\",",
    "  \"description\":",
    "    \"Registrar una prescripción.\",",
    "  \"parameters\": {",
    "    \"type\": \"object\",",
    "    \"properties\": {",
    "      \"agente\":",
    "        {\"type\": \"Q\", \"desc\": \"doctor\"},",
    "      \"paciente\":",
    "        {\"type\": \"Q\"},",
    "      \"medicamento_prescrito\":",
    "        {\"type\": \"K\", \"desc\": \"fármaco\"},",
    "      \"frecuencia\": {\"type\": \"K\"},",
    "      \"momento\":    {\"type\": \"T\"}",
    "    },",
    "    \"required\": [\"agente\", \"paciente\",",
    "                 \"medicamento_prescrito\"]",
    "  }",
    "}",
]
for i, line in enumerate(fn_lines):
    ax.text(right_x + 0.25, top_y - 1.1 - i * 0.25, line,
            ha="left", va="center", fontsize=8.0,
            color=INK, family="monospace")

# Flechas de correspondencia entre los campos clave
def correspondence(y_l, y_r, label):
    arr = FancyArrowPatch((left_x + col_w + 0.05, y_l),
                          (right_x - 0.05, y_r),
                          arrowstyle="-|>", mutation_scale=10,
                          color="#9ca3af", linewidth=1.0)
    ax.add_patch(arr)
    midx = (left_x + col_w + right_x) / 2
    midy = (y_l + y_r) / 2
    ax.text(midx, midy + 0.20, label,
            ha="center", va="center", fontsize=8,
            style="italic", color="#6b7280")

# verb → name
correspondence(top_y - 1.1, top_y - 1.45, "")

# Pie
ax.text(7.5, 0.45,
        "Misma información, dos formatos. Para exponer un universo WQuestions a un LLM,\n"
        "solo hay que exportar el lexicon como catálogo de funciones — sin código adaptador.",
        ha="center", va="center", fontsize=10, style="italic", color="#6b7280")

out = os.path.join(os.path.dirname(__file__), "..", "png",
                   "36_lexicon_function_schema.png")
plt.savefig(out, dpi=200, bbox_inches="tight", facecolor="#ffffff")
plt.close(fig)
print(f"  ✓ {out}")
