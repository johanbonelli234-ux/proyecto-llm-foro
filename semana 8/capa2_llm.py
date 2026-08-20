"""
Capa 2: Construcción de prompts para el LLM y parseo de respuestas
--------------------------------------------------------------------
Esta capa es responsable de:
  1. Construir los prompts que se envían al modelo (funciones construir_prompt_*).
  2. Invocar la API de Anthropic (_llamar_llm).
  3. Parsear la respuesta -siempre en formato JSON- hacia estructuras de
     datos de Python (funciones clasificar_mensaje, resumir_temas,
     evaluar_portafolio).

No se implementa ningún algoritmo de PLN propio: todo el análisis de
lenguaje natural (clasificación, sentimiento, resumen, evaluación de
calidad) lo realiza el LLM. Esta capa solo empaqueta la pregunta y
desempaqueta la respuesta.
"""

import json
from dataclasses import dataclass
from typing import List

import anthropic

from capa1_carga import MensajeForo
from config import MAX_TOKENS, MODEL, obtener_api_key

CATEGORIAS_VALIDAS = {"pregunta", "respuesta", "off-topic", "retroalimentacion"}
SENTIMIENTOS_VALIDOS = {"positivo", "negativo", "neutro"}


class ErrorDeLLM(Exception):
    """Se lanza cuando la llamada al LLM falla o su respuesta no se puede interpretar."""


@dataclass
class AnalisisMensaje:
    """Resultado del análisis de un único mensaje de foro."""

    mensaje: MensajeForo
    categoria: str
    sentimiento: str
    necesita_ayuda: bool
    justificacion: str


@dataclass
class ResumenTemas:
    """Resultado del resumen de temas de un conjunto de mensajes."""

    temas: List[str]
    descripcion: str


@dataclass
class EvaluacionPortafolio:
    """Resultado de la evaluación de calidad de un portafolio."""

    coherencia: int
    estructura: int
    uso_conceptos: int
    comentario: str

    @property
    def puntaje_total(self) -> float:
        return (self.coherencia + self.estructura + self.uso_conceptos) / 3


# ---------------------------------------------------------------------------
# Cliente de la API
# ---------------------------------------------------------------------------

def crear_cliente() -> anthropic.Anthropic:
    """Crea el cliente de la API de Anthropic usando la clave configurada en el entorno."""
    return anthropic.Anthropic(api_key=obtener_api_key())


# ---------------------------------------------------------------------------
# Construcción de prompts
# ---------------------------------------------------------------------------

def construir_prompt_clasificacion(texto: str) -> str:
    """Construye el prompt para clasificar un único mensaje de foro."""
    return f"""Eres un asistente que analiza mensajes de un foro académico universitario.

Analiza el siguiente mensaje y responde ÚNICAMENTE con un objeto JSON válido
(sin texto adicional antes o después, sin bloques de código markdown), con
esta estructura exacta:

{{
  "categoria": "pregunta | respuesta | off-topic | retroalimentacion",
  "sentimiento": "positivo | negativo | neutro",
  "necesita_ayuda": true o false,
  "justificacion": "una frase breve (máximo 20 palabras) explicando la clasificación"
}}

Definiciones de categoría:
- pregunta: el estudiante pide información, aclaración o ayuda.
- respuesta: el estudiante responde a una pregunta o aporta una solución.
- off-topic: el mensaje no está relacionado con el contenido académico del foro.
- retroalimentacion: el estudiante da retroalimentación sobre el trabajo de otro o del curso.

"necesita_ayuda" debe ser true si el mensaje muestra confusión persistente,
frustración o una emoción negativa que sugiera que el estudiante necesita
apoyo docente.

Mensaje a analizar:
\"\"\"
{texto}
\"\"\"
"""


def construir_prompt_resumen(mensajes: List[MensajeForo]) -> str:
    """Construye el prompt para resumir los temas principales de varios mensajes."""
    cuerpo = "\n".join(f"{i + 1}. ({m.usuario}) {m.texto}" for i, m in enumerate(mensajes))
    return f"""Eres un asistente que analiza la actividad de un foro académico.

A continuación hay una lista numerada de mensajes de distintos estudiantes.
Identifica entre 3 y 5 temas principales discutidos y responde ÚNICAMENTE
con un objeto JSON válido (sin texto adicional, sin bloques de código
markdown) con esta estructura:

{{
  "temas": ["tema 1", "tema 2", "..."],
  "descripcion": "un párrafo breve (máximo 60 palabras) resumiendo de qué trató la discusión en general"
}}

Mensajes:
{cuerpo}
"""


def construir_prompt_evaluacion_portafolio(texto: str) -> str:
    """Construye el prompt para evaluar la calidad de un fragmento de portafolio."""
    return f"""Eres un asistente que evalúa portafolios digitales de estudiantes de
forma pedagógica y constructiva.

Evalúa el siguiente fragmento de portafolio en tres dimensiones, cada una
con una nota de 1 (muy deficiente) a 5 (excelente):
- coherencia: qué tan bien conectadas y lógicas son las ideas.
- estructura: si el texto tiene una organización clara (introducción, desarrollo, cierre).
- uso_conceptos: si aplica correctamente los conceptos propios de la asignatura.

Responde ÚNICAMENTE con un objeto JSON válido (sin texto adicional, sin
bloques de código markdown) con esta estructura:

{{
  "coherencia": 1-5,
  "estructura": 1-5,
  "uso_conceptos": 1-5,
  "comentario": "retroalimentación breve y constructiva para el estudiante (máximo 60 palabras)"
}}

Fragmento de portafolio:
\"\"\"
{texto}
\"\"\"
"""


# ---------------------------------------------------------------------------
# Llamada al LLM y parseo
# ---------------------------------------------------------------------------

def _llamar_llm(cliente: anthropic.Anthropic, prompt: str) -> str:
    """Envía un prompt al modelo y devuelve el texto de la respuesta."""
    try:
        respuesta = cliente.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            messages=[{"role": "user", "content": prompt}],
        )
    except anthropic.APIError as e:
        raise ErrorDeLLM(f"Error al llamar a la API de Anthropic: {e}") from e

    texto = "".join(
        bloque.text for bloque in respuesta.content if getattr(bloque, "type", None) == "text"
    )
    if not texto:
        raise ErrorDeLLM("La respuesta del modelo no contenía texto.")
    return texto


def _parsear_json(texto_respuesta: str) -> dict:
    """Convierte la respuesta de texto del modelo en un diccionario Python."""
    limpio = texto_respuesta.strip()
    if limpio.startswith("```"):
        limpio = limpio.strip("`")
        if limpio.lower().startswith("json"):
            limpio = limpio[4:]
        limpio = limpio.strip()

    try:
        return json.loads(limpio)
    except json.JSONDecodeError as e:
        raise ErrorDeLLM(
            f"No se pudo interpretar la respuesta del modelo como JSON: {e}\n"
            f"Respuesta recibida: {texto_respuesta!r}"
        ) from e


# ---------------------------------------------------------------------------
# Funciones de análisis (API pública de la Capa 2)
# ---------------------------------------------------------------------------

def clasificar_mensaje(cliente: anthropic.Anthropic, mensaje: MensajeForo) -> AnalisisMensaje:
    """
    Clasifica un mensaje de foro en una categoría, detecta su sentimiento y
    determina si el estudiante podría necesitar ayuda.

    Cumple el entregable mínimo del proyecto (clasificación en pregunta /
    respuesta / otro) y lo extiende con categorías adicionales, sentimiento
    y detección de estudiantes que necesitan apoyo.
    """
    prompt = construir_prompt_clasificacion(mensaje.texto)
    respuesta_texto = _llamar_llm(cliente, prompt)
    datos = _parsear_json(respuesta_texto)

    categoria = str(datos.get("categoria", "")).strip().lower()
    if categoria not in CATEGORIAS_VALIDAS:
        categoria = "otro"

    sentimiento = str(datos.get("sentimiento", "")).strip().lower()
    if sentimiento not in SENTIMIENTOS_VALIDOS:
        sentimiento = "neutro"

    return AnalisisMensaje(
        mensaje=mensaje,
        categoria=categoria,
        sentimiento=sentimiento,
        necesita_ayuda=bool(datos.get("necesita_ayuda", False)),
        justificacion=str(datos.get("justificacion", "")).strip(),
    )


def resumir_temas(cliente: anthropic.Anthropic, mensajes: List[MensajeForo]) -> ResumenTemas:
    """Genera un resumen de los temas principales discutidos en un conjunto de mensajes."""
    prompt = construir_prompt_resumen(mensajes)
    respuesta_texto = _llamar_llm(cliente, prompt)
    datos = _parsear_json(respuesta_texto)

    temas = datos.get("temas", [])
    if not isinstance(temas, list):
        temas = []

    return ResumenTemas(
        temas=[str(t) for t in temas],
        descripcion=str(datos.get("descripcion", "")).strip(),
    )


def evaluar_portafolio(cliente: anthropic.Anthropic, texto: str) -> EvaluacionPortafolio:
    """Evalúa un fragmento de portafolio en coherencia, estructura y uso de conceptos."""
    prompt = construir_prompt_evaluacion_portafolio(texto)
    respuesta_texto = _llamar_llm(cliente, prompt)
    datos = _parsear_json(respuesta_texto)

    def _nota(valor) -> int:
        try:
            n = int(valor)
        except (TypeError, ValueError):
            n = 3
        return min(5, max(1, n))

    return EvaluacionPortafolio(
        coherencia=_nota(datos.get("coherencia")),
        estructura=_nota(datos.get("estructura")),
        uso_conceptos=_nota(datos.get("uso_conceptos")),
        comentario=str(datos.get("comentario", "")).strip(),
    )
