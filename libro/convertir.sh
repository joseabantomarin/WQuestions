#!/bin/bash
# Conversión del manuscrito Markdown → .docx
# Requiere: pandoc instalado (https://pandoc.org/installing.html)

set -e

LIBRO_DIR="$(cd "$(dirname "$0")" && pwd)"
MANUSCRITO_DIR="$LIBRO_DIR/manuscrito"
OUTPUT_DIR="$LIBRO_DIR/docx"

mkdir -p "$OUTPUT_DIR"

if ! command -v pandoc &> /dev/null; then
    echo "Error: pandoc no está instalado."
    echo ""
    echo "Para instalarlo:"
    echo "  Opción 1: descarga el .pkg desde https://github.com/jgm/pandoc/releases"
    echo "  Opción 2: instala Homebrew y luego 'brew install pandoc'"
    exit 1
fi

echo "Convirtiendo capítulos individuales..."
for md in "$MANUSCRITO_DIR"/*.md; do
    nombre=$(basename "$md" .md)
    pandoc "$md" -o "$OUTPUT_DIR/$nombre.docx" --standalone
    echo "  ✓ $nombre.docx"
done

echo ""
echo "Generando manuscrito completo..."
pandoc "$MANUSCRITO_DIR"/*.md \
    -o "$OUTPUT_DIR/manuscrito_completo.docx" \
    --standalone \
    --toc \
    --toc-depth=2 \
    --metadata title="Las preguntas como coordenadas" \
    --metadata author="WQuestions"

echo "  ✓ manuscrito_completo.docx"
echo ""
echo "Documentos generados en: $OUTPUT_DIR"
echo "Abre con: open $OUTPUT_DIR/manuscrito_completo.docx"
