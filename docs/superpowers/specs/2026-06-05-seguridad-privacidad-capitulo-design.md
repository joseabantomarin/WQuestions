# Capítulo «Seguridad y privacidad en el grafo compartido» — Diseño

**Fecha:** 2026-06-05
**Tipo:** Capítulo nuevo del libro WQuestions + 4 diagramas + renumeración.

## Objetivo

Escribir un capítulo propio que confronte de frente la objeción más seria al modelo:
si todo se construye sobre un grafo compartido con identidad estable, ¿no es eso una
máquina de vigilancia? Resolverlo desde la propia teoría (federación, permiso-como-hecho,
redacción por eje) y admitir con honestidad el frente abierto (inferencia/agregación).

## Decisiones (aprobadas con el autor)

- **Ubicación:** nuevo **Capítulo 27**, entre 26 (reflexiva) y *Qué falta*.
  Arco: *funciona* → *pero la realidad exige gobierno* → *qué falta* → *cierre*.
- **Anécdota de apertura:** cruce abusivo banco↔clínica. La misma paciente del libro pide
  un seguro/crédito; la aseguradora cruza y ve su arritmia, le sube la prima. *El mismo grafo
  que a las dos de la mañana le salvó la vida, a las diez de la mañana le niega la cobertura.*
- **Profundidad:** conceptual + técnicas nombradas (crypto-shredding, seudónimos pareados,
  privacidad diferencial) con analogías y unas pocas tripletas de ejemplo. Sin código pesado.

## Título

**Capítulo 27 — Quién puede preguntar qué: seguridad y privacidad en el grafo compartido.**
(El título usa la gramática del libro: el permiso de acceso es, él mismo, un hecho de quién/qué.)

## Estructura del capítulo

1. **La otra cara de la moneda** — la anécdota del cruce abusivo; la tensión sin suavizar.
2. **El malentendido que hay que deshacer** — el grafo compartido es un *idioma*, no una
   *base central*. Federación: cada tenedor guarda lo suyo; lo común es la pregunta. La escena
   del médico (Cap 16 / Conclusión) = publicación autorizada, no lectura global. → Diagrama 51.
3. **El permiso es un hecho** — ventaja estructural: el control de acceso se modela en el mismo
   idioma. Permiso/consentimiento como situaciones reificadas; revocación que **gana por D6**;
   la **auditoría sale gratis** (cada acceso es otra situación consultable). Unas tripletas. → Diagrama 52.
4. **Redacción por eje** — granularidad quirúrgica: mostrar que una transacción ocurrió
   (*qué/cuándo*) ocultando el *cuánto* y la contraparte. → Diagrama 53.
5. **Las tensiones crudas (honestidad):**
   - D6 «nunca olvida» vs. derecho al olvido → vigencia lógica vs. borrado físico; **crypto-shredding**;
     el modelo sabe en qué eje vive el PII → borrado dirigido más factible que el blob relacional.
   - Identidad estable = arma y herramienta → **seudónimos pareados** + el «enchufe» de URIs (Cap 4).
   - El frente abierto: **inferencia y agregación** → k-anonimato / privacidad diferencial son
     mitigaciones, no soluciones. Puente directo a «Qué falta» (Cap 28). → Diagrama 54.
6. **Veredicto / cierre** — idioma no base central; privacidad en el mismo modelo; control fino
   y borrado dirigido más factibles que lo relacional; pero la vinculabilidad hace de la inferencia
   el riesgo central. *Una arquitectura que no piensa la privacidad desde el día uno no merece adoptarse.*

## Diagramas (matplotlib, estilo existente, núms. 51–54)

- **51 — Federación vs. base central:** izq. cilindro único donde todos leen (✗ rojo);
  der. islas que guardan lo suyo pero hablan el mismo idioma, unidas por puentes de consentimiento (✓ verde).
- **52 — El permiso como situación reificada:** nodo-permiso con ejes (Q quién · O qué situación ·
  M puede_ver · T vigencia), idéntico en forma a cualquier otro hecho.
- **53 — Redacción por eje:** una situación con ejes visibles (verde) y otros bajo candado (*cuánto*, *quién*).
- **54 — El ataque por agregación:** hechos inocuos por separado que, combinados, revelan una identidad (rojo).

## Renumeración y referencias

**Renombrar archivos (git mv, en orden inverso para evitar colisión):**
- `31_el_autor.md` → `32_el_autor.md`
- `30_anexo_prototipo.md` → `31_anexo_prototipo.md`
- `29_anexo_codigo.md` → `30_anexo_codigo.md`
- `28_conclusion.md` → `29_conclusion.md`
- `27_que_falta.md` → `28_que_falta.md` (título interno «Capítulo 27» → «Capítulo 28»)
- **Nuevo:** `27_seguridad_privacidad.md`

**Referencias a *Qué falta* → pasan a «28» (varias estaban en 26/27, desactualizadas):**
- `11_verbo_signatura.md:104` «Capítulo 27» → 28
- `21_minera.md` ×4 («cap. 26» pendientes) → 28
- `22_sistema_existente_yaku.md` ×2 («cap. 26») → 28
- `24_llms.md:239` «capítulo 27» → 28
- `26_prueba_reflexiva.md:47` «Capítulo 27» → 28
- `29_conclusion.md` («El capítulo 27 lo enumeró») → 28
- `31_anexo_prototipo.md` ×4 («capítulo 27») → 28

**Referencias a la reflexiva → se quedan en «26»:**
- `28_que_falta.md:113` «(Capítulo 26)» — sin cambio
- `30_anexo_codigo.md:363` «Capítulo 26» — sin cambio

**Introducción:** frase de Parte VI «Capítulos 24 al 27» → «24 al 29», agregando el beat de
seguridad/privacidad a la descripción del recorrido.

**Sweep final:** `grep` de refs cruzadas por número tras renumerar, para cazar rezagos.

## Build

- Diagramas: `libro/diagrams/src/51..54_*.py` → `./render_diagrams.sh` → `png/`.
- PDF: `python3 libro/generar_pdf.py` (descubre `manuscrito/*.md` con `sorted(glob)` — el nuevo
  archivo `27_*` ordena solo).

## No incluido (YAGNI)

- No se implementa control de acceso en el prototipo Python (es un capítulo conceptual del libro).
- No se tocan los anexos salvo la renumeración y las refs.
