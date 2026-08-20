"""
Configuración central del proyecto.

El modelo se puede sobrescribir con la variable de entorno MODEL_LLM,
por ejemplo para usar un modelo más económico durante pruebas:
    export MODEL_LLM="claude-haiku-4-5-20251001"
"""

import os

API_KEY_ENV_VAR = "ANTHROPIC_API_KEY"
MODEL = os.environ.get("MODEL_LLM", "claude-sonnet-4-6")
MAX_TOKENS = 1024


def obtener_api_key() -> str:
    """Obtiene la clave de la API de Anthropic desde el entorno."""
    api_key = os.environ.get(API_KEY_ENV_VAR)
    if not api_key:
        raise EnvironmentError(
            f"No se encontró la variable de entorno {API_KEY_ENV_VAR}.\n"
            "Configúrala con tu clave de la API de Anthropic antes de ejecutar el programa.\n\n"
            "  Linux / macOS:      export ANTHROPIC_API_KEY='tu_clave_aqui'\n"
            "  Windows PowerShell:  $env:ANTHROPIC_API_KEY='tu_clave_aqui'\n\n"
            "Puedes obtener una clave en https://console.anthropic.com/"
        )
    return api_key
