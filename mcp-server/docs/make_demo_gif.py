"""Genera docs/demo.gif: un GIF animado estilo terminal que revela paso a paso
el demo real de WQuestions (spa -> barberia, las mismas 7 preguntas), con
efecto de maquina de escribir en el texto azul.

Requisitos:
    - Pillow:  pip install pillow
    - Fuente Menlo (viene con macOS). En otro SO, cambia MENLO por una .ttf
      monoespaciada disponible (ej. DejaVu Sans Mono).

Uso:
    python make_demo_gif.py        # regenera docs/demo.gif junto a este script

Los textos del demo estan en LINES; ajusta STEP/TYPE_MS/HOLD para el ritmo y
W/H para el tamano. Las salidas mostradas son las reales del motor wq.
"""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "demo.gif")

# --- Lienzo y tema (GitHub dark) --------------------------------------------
W, H = 1060, 720
PAD_X, TOP = 40, 92           # margenes; TOP deja sitio a la barra de ventana
LH = 30                        # alto de linea
BG = (13, 17, 23)             # #0d1117
CARD = (22, 27, 34)           # barra de ventana #161b22
BORDER = (48, 54, 61)         # #30363d
C_TITLE = (240, 246, 252)     # casi blanco
C_TEXT = (201, 209, 217)      # #c9d1d9
C_YOU = (88, 166, 255)        # #58a6ff azul (lo que escribe el usuario)
C_TOOL = (139, 148, 158)      # #8b949e gris apagado (llamadas a tools)
C_OK = (63, 185, 80)          # #3fb950 verde (resultados)
C_FOOT = (210, 168, 255)      # #d2a8ff violeta (remate)

MENLO = "/System/Library/Fonts/Menlo.ttc"   # macOS; cambia en otro SO
f_body = ImageFont.truetype(MENLO, 21, index=0)
f_bold = ImageFont.truetype(MENLO, 21, index=1)
f_title = ImageFont.truetype(MENLO, 25, index=1)
f_chrome = ImageFont.truetype(MENLO, 15, index=0)

# (texto, estilo). estilo controla color y fuente. Todo en INGLES: se usan
# los nombres reales de las tools y las palabras-pregunta (who/where/whom)
# en vez de los ids de rol internos del motor (que estan en espanol).
LINES = [
    ("WQuestions — model any domain in 7 questions", "title"),
    ("", "gap"),
    ("❯ Load the spa example, then show me the model.", "you"),
    ("    load_example(\"spa\")  ·  show_model()", "tool"),
    ("  ✓ 7 entities, 9 facts — a spa, modeled on the 7 axes", "ok"),
    ("", "gap"),
    ("❯ Who visited Spa Oasis?", "you"),
    ("    ask · where = Spa Oasis  →  who?", "tool"),
    ("  ✓ Ana (twice), Beto", "ok"),
    ("", "gap"),
    ("❯ Now model a barbershop: Diego cut Marco's hair", "you"),
    ("  at Barber Kings on 2025-06-11.", "you"),
    ("    add_entity ×3  ·  assert_situation(\"haircut\", ...)", "tool"),
    ("  ✓ saved — no schema, no new tool, verb auto-registered", "ok"),
    ("", "gap"),
    ("❯ Who did Diego serve, and where?", "you"),
    ("    ask · who = Diego  →  whom? where?", "tool"),
    ("  ✓ Marco, at Barber Kings", "ok"),
    ("", "gap"),
    ("Same 7 questions.  Same tools.  Any domain.  Zero schema.", "foot"),
]

STYLE = {
    "title": (C_TITLE, f_title),
    "you":   (C_YOU, f_bold),
    "tool":  (C_TOOL, f_body),
    "ok":    (C_OK, f_body),
    "foot":  (C_FOOT, f_bold),
    "gap":   (C_TEXT, f_body),
}


def base():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    # barra de ventana
    d.rectangle([0, 0, W, 56], fill=CARD)
    d.line([0, 56, W, 56], fill=BORDER)
    for i, col in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        cx = 26 + i * 22
        d.ellipse([cx, 21, cx + 13, 34], fill=col)
    d.text((W // 2, 28), "wquestions  ·  MCP server", font=f_chrome,
           fill=C_TOOL, anchor="mm")
    return img, d


def render(completed, partial=None):
    """Dibuja las lineas ya completas; si `partial`=(text,style,k) dibuja la
    linea actual solo hasta k caracteres, con un cursor (efecto maquina de
    escribir para el texto azul)."""
    img, d = base()
    y = TOP
    for text, style in completed:
        if style == "gap":
            y += LH // 2 + 4
            continue
        color, font = STYLE[style]
        d.text((PAD_X, y), text, font=font, fill=color)
        if style == "title":
            y += LH
            d.line([PAD_X, y - 4, W - PAD_X, y - 4], fill=BORDER)
            y += 8
        else:
            y += LH
    if partial is not None:
        text, style, k = partial
        color, font = STYLE[style]
        shown = text[:k]
        d.text((PAD_X, y), shown, font=font, fill=color)
        cx = PAD_X + d.textlength(shown, font=font)   # cursor al final
        d.rectangle([cx + 2, y + 3, cx + 12, y + LH - 6], fill=color)
    return img


# --- Animacion --------------------------------------------------------------
STEP = 3          # caracteres por frame (mas bajo = tecleo mas suave, mas peso)
TYPE_MS = 20      # duracion de cada frame de tecleo (alta velocidad)
HOLD = {"title": 700, "tool": 460, "ok": 680, "foot": 320}


def build():
    frames, durations = [], []
    completed = []
    for text, style in LINES:
        if style == "gap":
            completed.append((text, style))
            continue
        if style == "you":
            # tecleo: revela STEP caracteres por frame, con cursor
            k = STEP
            while k < len(text):
                frames.append(render(completed, (text, style, k)))
                durations.append(TYPE_MS)
                k += STEP
            frames.append(render(completed, (text, style, len(text))))
            durations.append(TYPE_MS + 220)     # pausa breve al terminar la linea
            completed.append((text, style))
        else:
            completed.append((text, style))
            frames.append(render(completed))
            durations.append(HOLD[style])
    frames.append(render(completed))            # frame final completo
    durations.append(4200)
    return frames, durations


if __name__ == "__main__":
    frames, durations = build()
    frames[0].save(
        OUT, save_all=True, append_images=frames[1:],
        duration=durations, loop=0, optimize=True, disposal=2,
    )
    kb = os.path.getsize(OUT) / 1024
    print(f"OK -> {OUT}")
    print(f"{len(frames)} frames, {W}x{H}, {kb:.0f} KB")
