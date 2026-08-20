# Informe de lecciones aprendidas — Grupo 8 y 9

> Plantilla para el entregable de la Semana 8. Las secciones marcadas con
> `[Completar]` deben llenarse con la experiencia real del equipo durante
> las semanas 2, 4 y 6; el resto ya refleja lo implementado en el código
> final de este repositorio.

## 1. Integrantes del grupo

- [Completar: nombres de los integrantes de los grupos 8 y 9]

## 2. Resumen del proyecto

Herramienta de línea de comandos que usa un LLM (Claude, vía la API de
Anthropic) para analizar mensajes de foros académicos y fragmentos de
portafolios digitales. Clasifica mensajes en cuatro categorías (pregunta,
respuesta, off-topic, retroalimentación), detecta sentimiento, identifica
estudiantes que podrían necesitar ayuda, resume los temas principales de
un foro y evalúa portafolios en coherencia, estructura y uso de conceptos.

## 3. Evolución del proyecto por hito

### Semana 2 — Diseño de arquitectura por capas

- [Completar: decisiones tomadas al diseñar el diagrama de capas, qué
  alternativas se consideraron, qué cambió respecto al diseño original]

### Semana 4 — Prototipo de Capa 1 y Capa 2 (versión mock)

- [Completar: cómo se simuló la Capa 2 antes de integrar el LLM real, qué
  supuestos se hicieron sobre el formato de entrada y de las respuestas]

### Semana 6 — Integración con el LLM + Capa 3 básica

- [Completar: primeras pruebas reales contra la API, problemas de
  formato de respuesta, primeras versiones del CLI]

### Semana 8 — Proyecto final

Se consolidó la arquitectura de tres capas:

- **Capa 1** (`capa1_carga.py`): carga y valida archivos de foro
  (formato `usuario|fecha|mensaje`) y de portafolio (texto plano).
- **Capa 2** (`capa2_llm.py`): construye los prompts, llama a la API de
  Anthropic y parsea las respuestas JSON hacia estructuras de datos
  tipadas (`AnalisisMensaje`, `ResumenTemas`, `EvaluacionPortafolio`).
- **Capa 3** (`main.py`): CLI con dos subcomandos (`foro`, `portafolio`)
  que orquesta las capas anteriores y presenta los resultados.

Se agregaron pruebas unitarias (`tests/test_clasificacion.py`) con
respuestas de LLM simuladas, para poder verificar el parseo y el manejo
de errores sin depender de una clave de API real ni incurrir en costos de
API durante el desarrollo.

## 4. Decisiones técnicas clave

- **Todo el análisis de lenguaje natural lo realiza el LLM**: no se
  implementó ningún algoritmo propio de clasificación o análisis de
  sentimiento; la Capa 2 solo construye prompts y parsea JSON.
- **Formato de respuesta forzado a JSON**: cada prompt exige una
  estructura JSON exacta, lo que simplifica el parseo y reduce la
  ambigüedad frente a respuestas en texto libre.
- **Valores por defecto ante respuestas inesperadas**: si el LLM devuelve
  una categoría o sentimiento fuera del conjunto esperado, el sistema usa
  un valor por defecto (`"otro"` / `"neutro"`) en lugar de fallar, para
  que un análisis inválido no interrumpa el procesamiento de todo el
  archivo.
- [Completar: otras decisiones específicas del equipo, por ejemplo el
  modelo elegido, el diseño del formato de entrada, etc.]

## 5. Dificultades encontradas

- [Completar: problemas reales del equipo — por ejemplo, respuestas del
  LLM que no seguían el formato JSON pedido, ambigüedad en la definición
  de "necesita ayuda", límites de tokens, costos de API, etc.]

## 6. Qué se haría diferente

- [Completar: aprendizajes retrospectivos del equipo]

## 7. Extensiones no implementadas

Quedaron fuera del alcance de esta entrega (ver sección "Extensiones
posibles" del README):

- Nube de palabras a partir de los temas extraídos.
- Exportación de resultados a CSV/JSON.
- Evaluación de portafolios contra una rúbrica formal con múltiples
  criterios ponderados.

## 8. Conclusiones

- [Completar: conclusión general del equipo sobre el aprendizaje del
  curso — arquitectura por capas, integración con LLMs, diseño de
  prompts, etc.]
