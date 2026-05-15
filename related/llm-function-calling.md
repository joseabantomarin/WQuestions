# LLMs y representación estructurada — Function Calling, MCP, agentes 2026

Documento de referencia sobre la línea contemporánea (2024-2026) de **LLMs + representación estructurada de conocimiento**: function calling, tool use, agentic workflows, conexión con knowledge graphs. Es el puente operativo entre WQuestions y los modelos de lenguaje grandes, y el contexto donde la D8 (invisibilidad del catálogo canónico) cobra su máximo valor.

## Datos bibliográficos y recursos

- **Function Calling fundacionales**: OpenAI function calling (2023), Anthropic tool use (2023-2024).
- **Model Context Protocol (MCP)**: Anthropic, open spec para conexión entre LLMs y herramientas externas.
- **Surveys recientes**:
  - *LLM-Based Agents for Tool Learning: A Survey* (Springer DSE 2025).
  - *Function Calling: Structured Tool Use for LLMs* (Brenndoerfer 2025).
- **Investigación 2025-2026**:
  - *LLM-Supported Formal Knowledge Representation via PyIRK* (arXiv 2511.02759).
  - *PRISM: Dual View of LLM Reasoning through Semantic Flow and Latent Computation* (arXiv 2603.22754).
  - *LLM-Augmented Knowledge Representation Learning* (OpenReview 2025).
- **Industria**:
  - *From LLMs to Knowledge Graphs: Production-Ready Graph Systems* (Medium 2025).
  - *Weaving Knowledge Graphs and LLMs* (ScienceDirect 2025).
- **Benchmarks 2026**:
  - BenchLM.ai — agentic tool-use rankings.

## Motivación declarada

Los LLMs son excelentes generando texto pero deficientes en:
- Acceder a información actualizada (no en su training).
- Ejecutar operaciones con efectos (escribir, transferir, calcular).
- Razonar consistentemente sobre conocimiento estructurado.

**Function calling** y **tool use** son la respuesta dominante: el LLM emite invocaciones estructuradas (JSON con argumentos tipados) y un sistema externo ejecuta. Esto da al LLM acceso al mundo sin pedirle que lo memorice.

**Agentic workflows** combinan múltiples function calls en secuencias autónomas. **MCP** (Model Context Protocol) estandariza cómo herramientas externas se exponen al LLM.

**LLMs + knowledge graphs** combina el razonamiento simbólico estructurado con la flexibilidad lingüística — exactamente el espacio donde WQuestions se posiciona.

## Núcleo del paradigma

### Function calling

El LLM ve un schema JSON de funciones disponibles:

```json
{
  "name": "registrar_venta",
  "description": "Registra una transacción de venta",
  "parameters": {
    "type": "object",
    "properties": {
      "vendedor":     {"type": "string"},
      "comprador":    {"type": "string"},
      "producto":     {"type": "string"},
      "precio":       {"type": "number"},
      "moneda":       {"type": "string"},
      "momento":      {"type": "string", "format": "date-time"}
    },
    "required": ["vendedor", "comprador", "producto", "precio"]
  }
}
```

Cuando el usuario habla en NL ("Pedro vendió un libro a María por 20 soles ayer"), el LLM:
1. Extrae los argumentos del texto.
2. Emite un function call JSON con esos argumentos.
3. El sistema externo ejecuta.

### MCP (Model Context Protocol)

Estándar abierto para exponer herramientas a LLMs. Define:
- Cómo un servidor describe sus herramientas.
- Cómo el LLM las descubre dinámicamente.
- Cómo se manejan errores, autorización, contexto.

### Dynamic Tool Retrieval

Cuando hay muchas funciones disponibles, no caben todas en el prompt. Solución: índice semántico de funciones; el LLM busca las relevantes para la consulta actual.

### Agentic Guardrails (2026)

Capas de seguridad para function calling autónomo:
- **Semantic Firewall**: un LLM secundario monitorea las llamadas del principal y aborta si desvían de la intención del usuario.
- **Permission scoping**: cada función tiene scope de autorización.

## Características clave

- **JSON estructurado**: salida verificable, parseable, validable contra schemas.
- **Composabilidad**: múltiples function calls en cadena.
- **Paralelizable**: el LLM puede invocar varias funciones simultáneas.
- **Stateless por defecto**: cada llamada es independiente; el estado vive afuera.
- **Tipado fuerte**: los argumentos tienen tipos, restricciones, formato.

## Aplicaciones (2026)

- **Asistentes empresariales**: Claude/GPT integrados con SAP, Salesforce, sistemas internos.
- **Agentes de investigación**: leer papers, ejecutar análisis, generar reportes.
- **Sistemas de soporte**: clasificar tickets, buscar en KB, escalar.
- **Pipelines de ingesta**: extraer información estructurada de texto.

## Posicionamiento frente a WQuestions

| Aspecto | LLM + Function Calling | WQuestions |
|---|---|---|
| Unidad estructural | JSON schema por función | Hecho atómico + situación reificada |
| Vocabulario | Definido por cada función | Catálogo canónico D7 + lexicon |
| Tipado | JSON Schema | Signaturas en P, M |
| Persistencia | Externa (la función decide) | Implícita (en almacenamiento de hechos) |
| Composición | Secuencial / paralela de funciones | Mereológica (parte_de) + temporal (precede) |
| Inmutabilidad | No estándar | Convención |
| Razonamiento | Delegado al LLM o tool | Pendiente (motor de inferencia) |
| Validez temporal | No estándar | D9 |

## Convergencias importantes

- **D8 es function calling avant la lettre**: la arquitectura por capas de D8 (UI/NL → dialecto → lexicon → canónico) coincide con cómo el LLM convierte NL en function call. Layer 4 de D8 = el texto del usuario; Layer 1 de D8 = el JSON canónico.

- **El lexicon es un function schema**: cada entrada del `lexicon.md` con sus aliases es esencialmente un function schema:

  ```yaml
  # Equivalente function calling:
  name: registrar_venta
  description: "Registra una transacción de venta"
  parameters:
    vendedor (agente):    {description: "Quien vende",     type: Q}
    producto (tema):      {description: "Lo vendido",      type: O}
    comprador (benef.):   {description: "Quien compra",    type: Q}
    precio (por_cuanto):  {description: "Monto pagado",    type: N}
  ```

- **Function calling exige canonicalización estructurada**: si una empresa expone 200 funciones, el LLM necesita un schema canónico para no confundirlas. WQuestions provee exactamente esa estructura.

- **MCP y D8 son hermanos arquitectónicos**: MCP estandariza cómo herramientas exponen su interfaz; D8 estandariza cómo el conocimiento expone su modelo. Ambos delegan el canónico a un nivel inferior.

## Divergencias importantes

- **Función vs hecho**: function calling invoca acciones; WQuestions almacena hechos. Son operaciones distintas pero compatibles: una función puede ser "registrar_hecho_en_WQuestions".

- **Estado**: function calling es stateless por diseño; WQuestions es stateful (acumula hechos).

- **Razonamiento**: function calling delega el razonamiento al LLM mismo (que es probabilístico). WQuestions apunta a razonamiento simbólico verificable (cuando se implemente el motor de inferencia).

- **Escala temporal**: function calling es transaccional (una llamada, un momento); WQuestions modela historia completa.

## Qué tomar prestado

- **JSON Schema como serialización**: para implementar WQuestions, exponer las situaciones canónicas como JSON Schema permite integración directa con LLMs.

- **MCP como protocolo**: si WQuestions se construye como sistema, exponerlo vía MCP da inmediata accesibilidad para todos los LLMs principales.

- **El paradigma "LLM como capa 4 de D8"**: hacer explícito que el modo natural de interactuar con WQuestions es vía LLM. El usuario habla, el LLM canonicaliza, WQuestions almacena.

- **Dynamic Tool Retrieval para el lexicon**: cuando el lexicon crezca a miles de verbos, no caben todos en el prompt. Indexar semánticamente y recuperar dinámicamente.

- **Agentic Guardrails**: cuando los LLMs poblen WQuestions automáticamente, hay que validar que los hechos sean consistentes con D9, signaturas, etc.

- **PyIRK** (Python Imperative Representation of Knowledge): framework reciente con espíritu cercano a WQuestions. Vale estudiar la API.

## Qué NO tomar prestado

- **El stateless dogmático**: WQuestions necesita estado persistente. No copiar el patrón de "cada llamada es independiente".

- **El razonamiento probabilístico**: LLMs alucinan. WQuestions debe tener verificación simbólica explícita encima de cualquier input LLM.

- **El sesgo a JSON**: JSON Schema es buena serialización pero no es el modelo conceptual. WQuestions vive antes de JSON.

## Recomendación para WQuestions

Tres adiciones prácticas:

1. **Documentar D8 como base para "WQuestions sobre LLMs"**: el lexicon se vuelve un function schema; los aliases son descriptions; los roles canónicos son parameter names; el sistema canonicaliza JSON → hechos.

2. **Plan de exposición vía MCP**: una vez implementado, WQuestions expuesto por MCP es inmediatamente usable por todo agente LLM moderno.

3. **Capítulo en el libro sobre "WQuestions como infraestructura para IA conversacional"**: esto es el ángulo más vendible al mercado 2026. La promesa: "habla en español; el sistema entiende, almacena, consulta y razona estructuradamente".

## Conclusión

El paradigma 2024-2026 de **LLMs + function calling + agentic** es el contexto natural donde D8 tiene sentido pleno. Lo que motivó D8 (no obligar al usuario a aprender D7) se vuelve doblemente relevante cuando el "usuario" puede ser un LLM, porque:

- El LLM no aprende; consume schemas.
- El LLM emite JSON tipado; D8 le da el schema canónico.
- El LLM canonicaliza NL → estructura; D8 define qué estructura.

Para el libro y el proyecto, esta línea es:

1. **El gancho comercial / práctico**: WQuestions resuelve problemas reales que las empresas tienen hoy con LLMs.
2. **El puente al mercado**: cualquier integración con LLM se beneficia de WQuestions.
3. **Validación arquitectónica**: function calling como industria converge a la misma estructura que D8 propone.
4. **Roadmap claro**: exponer WQuestions vía MCP es el camino más corto a impacto.

Mientras los grandes proyectos académicos (Biolink, CIDOC) tardan años en adoptarse, WQuestions vía LLM+MCP puede llegar a producción en meses si se implementa con disciplina.
