#!/bin/bash
# Renderiza todos los diagramas-fuente a PNG.
# Cada *.py en diagrams/src/ es un script independiente que escribe a diagrams/png/.

set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
SRC="$DIR/diagrams/src"
PNG="$DIR/diagrams/png"

mkdir -p "$PNG"

if [ -z "$(ls -A "$SRC"/*.py 2>/dev/null)" ]; then
    echo "No hay diagramas en $SRC"
    exit 0
fi

echo "Renderizando diagramas..."
for py in "$SRC"/*.py; do
    python3 "$py"
done
echo "Listo. PNGs en $PNG"
