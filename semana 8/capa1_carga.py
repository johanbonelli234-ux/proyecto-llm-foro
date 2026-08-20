"""
Capa 1: Carga de datos
-----------------------
Responsable ÚNICAMENTE de leer los archivos de entrada (foro o portafolio)
y convertirlos en estructuras de datos que la Capa 2 pueda procesar.
No contiene ninguna lógica de LLM ni de presentación.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass
class MensajeForo:
    """Representa una intervención individual de un foro de discusión."""

    usuario: str
    fecha: str
    texto: str
    numero_linea: int

    def __str__(self) -> str:  # pragma: no cover - solo utilidad de depuración
        return f"[{self.numero_linea}] {self.usuario} ({self.fecha}): {self.texto[:60]}"


class ErrorDeCarga(Exception):
    """Se lanza cuando un archivo de entrada no existe o tiene un formato inválido."""


def cargar_foro(ruta: str) -> List[MensajeForo]:
    """
    Carga un archivo de foro.

    Formato esperado por línea:
        usuario|fecha|mensaje

    - Las líneas vacías se ignoran.
    - Las líneas que empiezan con '#' se tratan como comentarios y se ignoran
      (útil para documentar los archivos de ejemplo).

    Lanza ErrorDeCarga si el archivo no existe, está vacío o alguna línea
    no respeta el formato esperado.
    """
    archivo = Path(ruta)
    if not archivo.exists():
        raise ErrorDeCarga(f"El archivo '{ruta}' no existe.")

    mensajes: List[MensajeForo] = []
    with archivo.open(encoding="utf-8") as f:
        for numero_linea, linea in enumerate(f, start=1):
            linea = linea.rstrip("\n")
            if not linea.strip() or linea.strip().startswith("#"):
                continue

            partes = linea.split("|", maxsplit=2)
            if len(partes) != 3:
                raise ErrorDeCarga(
                    f"Línea {numero_linea} con formato inválido "
                    f"(se esperaba 'usuario|fecha|mensaje'): {linea!r}"
                )

            usuario, fecha, texto = (p.strip() for p in partes)
            if not texto:
                continue

            mensajes.append(
                MensajeForo(usuario=usuario, fecha=fecha, texto=texto, numero_linea=numero_linea)
            )

    if not mensajes:
        raise ErrorDeCarga(f"El archivo '{ruta}' no contiene mensajes válidos.")

    return mensajes


def cargar_portafolio(ruta: str) -> str:
    """Carga un fragmento de portafolio digital como texto continuo."""
    archivo = Path(ruta)
    if not archivo.exists():
        raise ErrorDeCarga(f"El archivo '{ruta}' no existe.")

    texto = archivo.read_text(encoding="utf-8").strip()
    if not texto:
        raise ErrorDeCarga(f"El archivo '{ruta}' está vacío.")

    return texto
