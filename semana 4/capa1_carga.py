"""
Capa 1 - Carga de datos
Lee un archivo de texto plano con mensajes de foro (formato: usuario;fecha;mensaje)
y los convierte en estructuras de datos manejables por las capas superiores.
"""

from dataclasses import dataclass
from typing import List


@dataclass
class MensajeForo:
    usuario: str
    fecha: str
    texto: str


def cargar_mensajes(ruta_archivo: str) -> List[MensajeForo]:
    """
    Lee el archivo línea por línea y devuelve una lista de MensajeForo.
    Cada línea debe tener el formato: usuario;fecha;mensaje
    Ignora líneas vacías o mal formateadas.
    """
    mensajes: List[MensajeForo] = []

    with open(ruta_archivo, "r", encoding="utf-8") as f:
        for numero_linea, linea in enumerate(f, start=1):
            linea = linea.strip()
            if not linea:
                continue

            partes = linea.split(";", maxsplit=2)
            if len(partes) != 3:
                print(f"[Aviso] Línea {numero_linea} ignorada (formato inválido): {linea}")
                continue

            usuario, fecha, texto = (p.strip() for p in partes)
            mensajes.append(MensajeForo(usuario=usuario, fecha=fecha, texto=texto))

    return mensajes


if __name__ == "__main__":
    # Prueba rápida de la Capa 1
    mensajes = cargar_mensajes("datos_foro.txt")
    for m in mensajes:
        print(m)
