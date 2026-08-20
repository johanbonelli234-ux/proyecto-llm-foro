#!/usr/bin/env python3
"""
Capa 3: Interfaz de línea de comandos (CLI)
--------------------------------------------
Punto de entrada del proyecto. Orquesta la Capa 1 (carga de datos) y la
Capa 2 (prompts al LLM + parseo de respuestas), y presenta los resultados
al usuario en la terminal.

Uso:
    python main.py foro <archivo> [--resumen]
    python main.py portafolio <archivo>

Ejemplos:
    python main.py foro ejemplos/foro_ejemplo.txt --resumen
    python main.py portafolio ejemplos/portafolio_ejemplo.txt
"""

import argparse
import sys

from capa1_carga import ErrorDeCarga, cargar_foro, cargar_portafolio
from capa2_llm import (
    ErrorDeLLM,
    clasificar_mensaje,
    crear_cliente,
    evaluar_portafolio,
    resumir_temas,
)


def imprimir_encabezado(texto: str) -> None:
    print("\n" + "=" * 70)
    print(texto)
    print("=" * 70)


def comando_foro(args: argparse.Namespace) -> int:
    """Carga un archivo de foro, clasifica cada mensaje y reporta hallazgos."""
    try:
        mensajes = cargar_foro(args.archivo)
    except ErrorDeCarga as e:
        print(f"Error al cargar el archivo: {e}", file=sys.stderr)
        return 1

    print(f"Se cargaron {len(mensajes)} mensajes desde '{args.archivo}'.")

    try:
        cliente = crear_cliente()
    except EnvironmentError as e:
        print(str(e), file=sys.stderr)
        return 1

    imprimir_encabezado("CLASIFICACIÓN DE MENSAJES")
    analisis = []
    estudiantes_con_ayuda = []

    for mensaje in mensajes:
        try:
            resultado = clasificar_mensaje(cliente, mensaje)
        except ErrorDeLLM as e:
            print(f"  [AVISO] No se pudo analizar el mensaje {mensaje.numero_linea}: {e}")
            continue

        analisis.append(resultado)
        marca_ayuda = "  ⚠️  NECESITA AYUDA" if resultado.necesita_ayuda else ""
        recorte = mensaje.texto[:80] + ("..." if len(mensaje.texto) > 80 else "")
        print(
            f"\n- {mensaje.usuario} ({mensaje.fecha}) -> "
            f"{resultado.categoria.upper()} / {resultado.sentimiento}{marca_ayuda}"
        )
        print(f'    "{recorte}"')
        print(f"    Justificación: {resultado.justificacion}")

        if resultado.necesita_ayuda:
            estudiantes_con_ayuda.append(mensaje.usuario)

    imprimir_encabezado("ESTUDIANTES QUE PODRÍAN NECESITAR AYUDA")
    if estudiantes_con_ayuda:
        for usuario in sorted(set(estudiantes_con_ayuda)):
            print(f"- {usuario}")
    else:
        print("Ningún estudiante mostró señales de necesitar ayuda adicional.")

    if args.resumen and analisis:
        imprimir_encabezado("RESUMEN DE TEMAS PRINCIPALES")
        try:
            resumen = resumir_temas(cliente, mensajes)
            for tema in resumen.temas:
                print(f"- {tema}")
            print(f"\n{resumen.descripcion}")
        except ErrorDeLLM as e:
            print(f"No se pudo generar el resumen de temas: {e}")

    return 0


def comando_portafolio(args: argparse.Namespace) -> int:
    """Carga un fragmento de portafolio y lo evalúa en tres dimensiones de calidad."""
    try:
        texto = cargar_portafolio(args.archivo)
    except ErrorDeCarga as e:
        print(f"Error al cargar el archivo: {e}", file=sys.stderr)
        return 1

    try:
        cliente = crear_cliente()
    except EnvironmentError as e:
        print(str(e), file=sys.stderr)
        return 1

    imprimir_encabezado("EVALUACIÓN DE PORTAFOLIO")
    try:
        evaluacion = evaluar_portafolio(cliente, texto)
    except ErrorDeLLM as e:
        print(f"No se pudo evaluar el portafolio: {e}", file=sys.stderr)
        return 1

    print(f"Coherencia:       {evaluacion.coherencia} / 5")
    print(f"Estructura:       {evaluacion.estructura} / 5")
    print(f"Uso de conceptos: {evaluacion.uso_conceptos} / 5")
    print(f"Puntaje general:  {evaluacion.puntaje_total:.1f} / 5")
    print(f"\nComentario:\n{evaluacion.comentario}")

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="main.py",
        description="Analiza foros de discusión o portafolios de estudiantes usando un LLM.",
    )
    subparsers = parser.add_subparsers(dest="comando", required=True)

    parser_foro = subparsers.add_parser("foro", help="Analiza un archivo de mensajes de foro.")
    parser_foro.add_argument(
        "archivo", help="Ruta al archivo de foro (formato usuario|fecha|mensaje)."
    )
    parser_foro.add_argument(
        "--resumen",
        action="store_true",
        help="Genera además un resumen de los temas principales discutidos.",
    )
    parser_foro.set_defaults(func=comando_foro)

    parser_portafolio = subparsers.add_parser(
        "portafolio", help="Evalúa un fragmento de portafolio digital."
    )
    parser_portafolio.add_argument("archivo", help="Ruta al archivo de texto del portafolio.")
    parser_portafolio.set_defaults(func=comando_portafolio)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
