# Libro WQuestions

Manuscrito en desarrollo. Estructura del directorio:

```
libro/
├── README.md                  — este archivo
├── propuesta_editorial.md     — para editoras / agentes literarios
├── esquema_capitulos.md       — outline detallado de los capítulos
├── manuscrito/                — capítulos numerados
│   ├── 00_introduccion.md
│   ├── 01_problema_torre_babel.md
│   ├── ...
└── convertir.sh               — script para generar .docx con pandoc
```

## Estado actual

| Pieza | Estado |
|---|---|
| Propuesta editorial | Borrador inicial |
| Esquema de capítulos | Borrador inicial |
| Introducción | Borrador inicial |
| Capítulos 1–21 | Pendientes |

## Flujo de trabajo

1. La redacción se hace en Markdown (rápido, iterativo, versionable).
2. Para generar versión Word: `./convertir.sh` (requiere pandoc instalado).
3. Para abrir directamente en Word: Word 365+ abre archivos `.md` con formato básico.

## Instalación de pandoc (cuando estés listo)

```bash
# Opción 1 — instalador oficial (recomendado, no requiere Homebrew):
# Descarga el .pkg de https://github.com/jgm/pandoc/releases
# Doble-click al .pkg, sigue el wizard.

# Opción 2 — instalando Homebrew primero:
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install pandoc
```

Después: `./convertir.sh` desde el directorio `libro/`.
