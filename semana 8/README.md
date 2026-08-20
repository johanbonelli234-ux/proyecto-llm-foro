# Analizador de foros y portafolios con LLM — Grupo 8 y 9

Proyecto final (Semana 8). Procesa mensajes de un foro académico o
fragmentos de portafolio digital y usa un LLM (Claude, vía la API de
Anthropic) para clasificarlos, resumir temas, detectar estudiantes que
podrían necesitar ayuda y evaluar la calidad de un portafolio.

Todo el procesamiento de lenguaje natural lo hace el LLM: el proyecto no
implementa algoritmos propios de PLN, solo construye prompts, llama a la
API y parsea las respuestas (JSON).

## Arquitectura por capas

```
main.py            Capa 3 — CLI: orquesta las capas 1 y 2, muestra resultados
capa2_llm.py        Capa 2 — construcción de prompts, llamada al LLM, parseo de JSON
capa1_carga.py       Capa 1 — carga de archivos (foro / portafolio)
config.py            Configuración (modelo, clave de API)
tests/                Pruebas unitarias de la Capa 2 con respuestas simuladas
ejemplos/             Archivos de ejemplo para probar el programa
```

Cada capa solo conoce a la capa inmediatamente inferior: `main.py` no
construye prompts ni parsea JSON directamente, y `capa2_llm.py` no sabe
leer archivos de disco.

## Funcionalidades implementadas

- **Clasificación de mensajes** en `pregunta`, `respuesta`, `off-topic` o
  `retroalimentacion` (cumple y extiende el entregable mínimo de 3
  categorías: pregunta / respuesta / otro).
- **Detección de sentimiento** (`positivo` / `negativo` / `neutro`).
- **Detección de estudiantes que podrían necesitar ayuda**, a partir de
  mensajes confusos o con carga emocional negativa.
- **Resumen de los temas principales** de un foro (`--resumen`).
- **Evaluación básica de portafolios** en coherencia, estructura y uso de
  conceptos (escala 1–5), con retroalimentación breve.

## Instalación

Requiere Python 3.9 o superior.

```bash
git clone <url-del-repositorio>
cd proyecto_foro_llm

python3 -m venv venv
source venv/bin/activate        # En Windows: venv\Scripts\activate

pip install -r requirements.txt
```

## Configuración de la clave de API

El programa necesita una clave de la API de Anthropic
(https://console.anthropic.com/) disponible en la variable de entorno
`ANTHROPIC_API_KEY`:

```bash
export ANTHROPIC_API_KEY="tu_clave_aqui"          # Linux / macOS
$env:ANTHROPIC_API_KEY="tu_clave_aqui"             # Windows PowerShell
```

Por defecto se usa el modelo `claude-sonnet-4-6`. Para usar un modelo más
económico durante pruebas, se puede sobrescribir con:

```bash
export MODEL_LLM="claude-haiku-4-5-20251001"
```

## Uso

### Analizar un foro

```bash
python main.py foro ejemplos/foro_ejemplo.txt
python main.py foro ejemplos/foro_ejemplo.txt --resumen
```

Muestra, para cada mensaje: categoría, sentimiento y justificación; al
final, la lista de estudiantes que podrían necesitar ayuda y (con
`--resumen`) los temas principales discutidos.

### Evaluar un portafolio

```bash
python main.py portafolio ejemplos/portafolio_ejemplo.txt
```

Muestra las notas de coherencia, estructura y uso de conceptos (1–5) y un
comentario de retroalimentación.

## Formato del archivo de foro

Una intervención por línea, campos separados por `|`:

```
usuario|fecha|mensaje
maria.lopez|2026-08-10|¿Alguien puede explicarme el ejercicio 4?
```

Las líneas vacías o que empiezan con `#` se ignoran.

## Formato del archivo de portafolio

Texto plano continuo (sin un formato de línea particular): el contenido
completo del archivo se envía al LLM para su evaluación.

## Ejecutar las pruebas

Las pruebas usan respuestas simuladas del LLM (no requieren clave de API):

```bash
python -m unittest discover -s tests -v
```

## Estructura de un mensaje analizado

Internamente, cada análisis de mensaje es un objeto `AnalisisMensaje` con
los campos: `mensaje` (el `MensajeForo` original), `categoria`,
`sentimiento`, `necesita_ayuda` y `justificacion`. El resumen de temas es
un `ResumenTemas` (`temas`, `descripcion`) y la evaluación de portafolio es
una `EvaluacionPortafolio` (`coherencia`, `estructura`, `uso_conceptos`,
`comentario`, `puntaje_total`).

## Extensiones posibles (no implementadas en esta entrega)

- Generar una nube de palabras a partir de los temas extraídos.
- Exportar los resultados a CSV o JSON para análisis posterior.
- Evaluar un portafolio completo contra una rúbrica formal (varias
  dimensiones adicionales, ponderaciones por criterio).
