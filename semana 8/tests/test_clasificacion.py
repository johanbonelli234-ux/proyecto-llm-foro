"""
Pruebas básicas de la Capa 2 usando respuestas simuladas (mock) del LLM,
para no depender de una clave de API real al ejecutar las pruebas.

Ejecutar con:
    python -m unittest discover -s tests -v
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from capa1_carga import MensajeForo  # noqa: E402
from capa2_llm import AnalisisMensaje, clasificar_mensaje  # noqa: E402

# Al menos 5 ejemplos, tal como pide el entregable mínimo del proyecto.
EJEMPLOS = [
    (
        "¿Cómo se resuelve el ejercicio 3?",
        '{"categoria": "pregunta", "sentimiento": "neutro", '
        '"necesita_ayuda": false, "justificacion": "pide ayuda puntual"}',
        "pregunta",
    ),
    (
        "La respuesta es aplicar la fórmula de Bayes.",
        '{"categoria": "respuesta", "sentimiento": "neutro", '
        '"necesita_ayuda": false, "justificacion": "aporta una solución"}',
        "respuesta",
    ),
    (
        "¿Alguien vio el partido de ayer?",
        '{"categoria": "off-topic", "sentimiento": "positivo", '
        '"necesita_ayuda": false, "justificacion": "no relacionado al curso"}',
        "off-topic",
    ),
    (
        "Muy buen aporte, me ayudó a entender el tema.",
        '{"categoria": "retroalimentacion", "sentimiento": "positivo", '
        '"necesita_ayuda": false, "justificacion": "elogia el aporte de otro"}',
        "retroalimentacion",
    ),
    (
        "Estoy perdido, no entiendo nada y ya me quiero rendir.",
        '{"categoria": "pregunta", "sentimiento": "negativo", '
        '"necesita_ayuda": true, "justificacion": "muestra frustración y confusión"}',
        "pregunta",
    ),
]


class TestClasificarMensaje(unittest.TestCase):
    def test_clasificacion_con_cinco_ejemplos(self):
        for i, (texto, respuesta_simulada, categoria_esperada) in enumerate(EJEMPLOS):
            mensaje = MensajeForo(
                usuario=f"user{i}", fecha="2026-08-01", texto=texto, numero_linea=i + 1
            )
            with patch("capa2_llm._llamar_llm", return_value=respuesta_simulada):
                resultado = clasificar_mensaje(cliente=None, mensaje=mensaje)

            self.assertIsInstance(resultado, AnalisisMensaje)
            self.assertEqual(resultado.categoria, categoria_esperada)
            self.assertIn(
                resultado.sentimiento, {"positivo", "negativo", "neutro"}
            )

    def test_respuesta_mal_formada_usa_valores_por_defecto(self):
        mensaje = MensajeForo(
            usuario="user0", fecha="2026-08-01", texto="texto cualquiera", numero_linea=1
        )
        respuesta_simulada = '{"categoria": "categoria_invalida", "sentimiento": "x"}'
        with patch("capa2_llm._llamar_llm", return_value=respuesta_simulada):
            resultado = clasificar_mensaje(cliente=None, mensaje=mensaje)

        self.assertEqual(resultado.categoria, "otro")
        self.assertEqual(resultado.sentimiento, "neutro")
        self.assertFalse(resultado.necesita_ayuda)

    def test_respuesta_con_bloque_markdown_se_parsea_igual(self):
        mensaje = MensajeForo(
            usuario="user1", fecha="2026-08-01", texto="¿Qué hora es la clase?", numero_linea=2
        )
        respuesta_simulada = (
            "```json\n"
            '{"categoria": "pregunta", "sentimiento": "neutro", '
            '"necesita_ayuda": false, "justificacion": "consulta administrativa"}'
            "\n```"
        )
        with patch("capa2_llm._llamar_llm", return_value=respuesta_simulada):
            resultado = clasificar_mensaje(cliente=None, mensaje=mensaje)

        self.assertEqual(resultado.categoria, "pregunta")


if __name__ == "__main__":
    unittest.main()
