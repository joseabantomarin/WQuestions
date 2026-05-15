"""Diagrama: la pila completa de WQuestions, de persistencia a aplicación.

Capas verticales: persistencia → núcleo modelo → motor + lexicon →
LLM via MCP → aplicación usuario. Cada capa puede evolucionar
independientemente.

Salida: ../png/40_pila_completa.png
"""

import os
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

INK = "#1f2937"

fig, ax = plt.subplots(figsize=(14, 9.5), dpi=200)
ax.set_xlim(0, 14)
ax.set_ylim(0, 9.5)
ax.axis("off")
fig.patch.set_facecolor("#ffffff")

# Título
ax.text(7, 9.10,
        "La pila completa: de la persistencia al usuario final",
        ha="center", va="center", fontsize=14, fontweight="bold", color=INK)
ax.text(7, 8.70,
        "Cinco capas. Cada una puede evolucionar independientemente — desacoplamiento por contrato.",
        ha="center", va="center", fontsize=10, style="italic", color="#6b7280")

# 5 capas, de abajo hacia arriba
layers = [
    {
        "name": "PERSISTENCIA",
        "subtitle": "almacenamiento físico",
        "options": "SQLite · Postgres+JSONB · Kùzu · Neo4j · RDF/SPARQL",
        "responsibility": "guardar individuos y hechos; indexación; bitemporalidad",
        "fill": "#e0e7ff", "edge": "#4f46e5",
    },
    {
        "name": "NÚCLEO WQUESTIONS",
        "subtitle": "modelo de datos",
        "options": "8 ejes (Q O L T N K P M) · catálogo D7 · D9 vigencia · hechos atómicos",
        "responsibility": "identidad estable · signaturas · ingesta · queries",
        "fill": "#dcfce7", "edge": "#15803d",
    },
    {
        "name": "EVALUADOR + LEXICON",
        "subtitle": "razonamiento + traducción",
        "options": "Datalog / SHACL / Python · Lexicon multi-dominio · dialectos",
        "responsibility": "disparar reglas · resolver polisemia · traducir aliases",
        "fill": "#fef3c7", "edge": "#b45309",
    },
    {
        "name": "INTERFAZ LLM (MCP)",
        "subtitle": "lenguaje natural ↔ función",
        "options": "Claude · GPT · Gemini · Llama · MCP server · function calling",
        "responsibility": "interpretar consulta · invocar función · componer respuesta",
        "fill": "#dbeafe", "edge": "#1d4ed8",
    },
    {
        "name": "APLICACIÓN",
        "subtitle": "experiencia del usuario final",
        "options": "asistente conversacional · dashboard · IDE · investigador · agente",
        "responsibility": "presentación · autenticación · auditoría · control de acceso",
        "fill": "#fee2e2", "edge": "#b91c1c",
    },
]

# Dibujar de abajo arriba
n = len(layers)
gap = 0.20
total_h = 7.6
layer_h = (total_h - gap * (n - 1)) / n
start_y = 0.7

for i, layer in enumerate(reversed(layers)):
    # reversed para que el índice 0 corresponda a la capa superior visualmente
    # mejor: dibujamos de abajo arriba con la lista original
    pass

# Redo: dibujo de abajo arriba en orden de la lista
for i, layer in enumerate(layers):
    y_bot = start_y + i * (layer_h + gap)
    y_top = y_bot + layer_h

    box = FancyBboxPatch((0.7, y_bot), 12.6, layer_h,
                         boxstyle="round,pad=0.05",
                         facecolor=layer["fill"], edgecolor=layer["edge"],
                         linewidth=1.8)
    ax.add_patch(box)

    # número de capa
    chip = FancyBboxPatch((0.95, y_top - 0.55), 0.55, 0.40,
                          boxstyle="round,pad=0.02",
                          facecolor=layer["edge"], edgecolor="none")
    ax.add_patch(chip)
    ax.text(1.225, y_top - 0.35, str(i + 1),
            ha="center", va="center", fontsize=11,
            color="white", fontweight="bold", family="monospace")

    # nombre + subtitle
    ax.text(1.75, y_top - 0.35, layer["name"],
            ha="left", va="center", fontsize=11.5, fontweight="bold",
            color=layer["edge"])
    ax.text(1.75, y_top - 0.62, layer["subtitle"],
            ha="left", va="center", fontsize=9, style="italic",
            color=layer["edge"])

    # opciones (lo que vive en esa capa)
    ax.text(7.5, y_top - 0.30, "opciones:",
            ha="left", va="center", fontsize=8.5,
            color="#374151", fontweight="bold")
    ax.text(7.5, y_top - 0.55, layer["options"],
            ha="left", va="center", fontsize=9,
            color="#374151", family="monospace")

    # responsabilidad
    ax.text(1.75, y_bot + 0.18, "responsabilidad:",
            ha="left", va="center", fontsize=8,
            color=layer["edge"], fontweight="bold")
    ax.text(3.10, y_bot + 0.18, layer["responsibility"],
            ha="left", va="center", fontsize=8.5,
            color="#374151", style="italic")

# Flechas indicando las dependencias
# (omito; el orden vertical ya implica la pila)

# Pie
ax.text(7, 0.30,
        "Cada capa expone un contrato; cualquier reemplazo respeta ese contrato. Esto permite migrar Postgres → Kùzu,",
        ha="center", va="center", fontsize=9, style="italic", color="#6b7280")
ax.text(7, 0.05,
        "Claude → GPT, o intercambiar el motor de inferencia, sin tocar las capas vecinas.",
        ha="center", va="center", fontsize=9, style="italic", color="#6b7280")

out = os.path.join(os.path.dirname(__file__), "..", "png",
                   "40_pila_completa.png")
plt.savefig(out, dpi=200, bbox_inches="tight", facecolor="#ffffff")
plt.close(fig)
print(f"  ✓ {out}")
