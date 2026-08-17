"""
Capa 2 - Construcción de prompts y parseo de respuestas
Esta versión NO llama a un LLM real. Se usa un "mock" que simula la respuesta
que en el entregable final vendría del modelo, para poder probar el flujo
completo (Capa 1 -> Capa 2 -> Capa 3) desde ya.

Cuando se integre el LLM real, solo hay que reemplazar la función
`llamar_llm_mock` por una llamada real a la API (ver plantilla comentada
al final del archivo).
"""

import json
from dataclasses import dataclass
from capa1_carga import MensajeForo

CATEGORIAS_VALIDAS = {"pregunta", "respuesta", "otro"}


@dataclass
class ResultadoClasificacion:
    usuario: str
    fecha: str
    texto: str
    categoria: str
    justificacion: str


def construir_prompt(mensaje: MensajeForo) -> str:
    """
    Construye el prompt que se enviaría al LLM para clasificar un mensaje.
    Se deja ya listo en formato instrucción + esquema de salida en JSON,
    para que la Capa 3 pueda parsear la respuesta sin ambigüedad.
    """
    prompt = f"""Eres un asistente que clasifica mensajes de un foro académico.
Clasifica el siguiente mensaje en UNA sola categoría: "pregunta", "respuesta" u "otro".

- "pregunta": el estudiante pide información o ayuda.
- "respuesta": el estudiante responde o ayuda a otro estudiante.
- "otro": mensaje off-topic, saludo, o que no encaja en las anteriores.

Mensaje del usuario "{mensaje.usuario}" ({mensaje.fecha}):
"{mensaje.texto}"

Responde ÚNICAMENTE con un JSON con este formato exacto:
{{"categoria": "pregunta|respuesta|otro", "justificacion": "breve explicación en una frase"}}
"""
    return prompt


def llamar_llm_mock(prompt: str, mensaje: MensajeForo) -> str:
    """
    MOCK: simula la respuesta de un LLM usando reglas simples sobre el texto
    original del mensaje (no sobre el prompt). Devuelve un string JSON,
    igual que lo haría la API real, para que el parseo (Capa 2) y la CLI
    (Capa 3) no necesiten cambiar cuando se conecte el LLM de verdad.
    """
    texto = mensaje.texto.lower()

    if "?" in mensaje.texto or texto.startswith(("¿", "como", "cómo", "que", "qué")):
        categoria = "pregunta"
        justificacion = "El mensaje contiene una pregunta explícita."
    elif any(p in texto for p in ["gracias", "se soluciona", "puedes", "prueba con", "te recomiendo"]):
        categoria = "respuesta"
        justificacion = "El mensaje responde o ayuda a otro usuario."
    else:
        categoria = "otro"
        justificacion = "El mensaje no es una pregunta ni una respuesta directa."

    respuesta_simulada = json.dumps(
        {"categoria": categoria, "justificacion": justificacion},
        ensure_ascii=False,
    )
    return respuesta_simulada


def parsear_respuesta(respuesta_json: str, mensaje: MensajeForo) -> ResultadoClasificacion:
    """
    Parsea la respuesta (string JSON) del LLM (o del mock) y la convierte
    en un ResultadoClasificacion. Valida que la categoría sea una de las
    permitidas; si no, cae a "otro".
    """
    try:
        datos = json.loads(respuesta_json)
        categoria = datos.get("categoria", "otro").strip().lower()
        justificacion = datos.get("justificacion", "").strip()
    except (json.JSONDecodeError, AttributeError):
        categoria = "otro"
        justificacion = "No se pudo interpretar la respuesta del modelo."

    if categoria not in CATEGORIAS_VALIDAS:
        categoria = "otro"

    return ResultadoClasificacion(
        usuario=mensaje.usuario,
        fecha=mensaje.fecha,
        texto=mensaje.texto,
        categoria=categoria,
        justificacion=justificacion,
    )


def clasificar_mensaje(mensaje: MensajeForo) -> ResultadoClasificacion:
    """
    Función de alto nivel que encadena: construir_prompt -> llamar LLM -> parsear.
    Es la única función que la Capa 3 (CLI) necesita invocar.
    """
    prompt = construir_prompt(mensaje)
    respuesta = llamar_llm_mock(prompt, mensaje)
    return parsear_respuesta(respuesta, mensaje)


# ---------------------------------------------------------------------------
# Plantilla para cuando se integre el LLM real (Anthropic API), no se ejecuta:
#
# import anthropic
# def llamar_llm_real(prompt: str) -> str:
#     client = anthropic.Anthropic(api_key="TU_API_KEY")
#     respuesta = client.messages.create(
#         model="claude-sonnet-4-6",
#         max_tokens=200,
#         messages=[{"role": "user", "content": prompt}],
#     )
#     return respuesta.content[0].text
# ---------------------------------------------------------------------------
