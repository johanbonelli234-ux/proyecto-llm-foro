"""
Demostración del prototipo (Capa 1 + Capa 2, sin LLM real).
Carga los mensajes del foro y muestra la clasificación de cada uno.
"""

from capa1_carga import cargar_mensajes
from capa2_procesamiento import clasificar_mensaje

RUTA_DATOS = "datos_foro.txt"


def main():
    mensajes = cargar_mensajes(RUTA_DATOS)
    print(f"Se cargaron {len(mensajes)} mensajes.\n")

    for mensaje in mensajes:
        resultado = clasificar_mensaje(mensaje)
        print(f"Usuario:      {resultado.usuario} ({resultado.fecha})")
        print(f"Mensaje:      {resultado.texto}")
        print(f"Categoría:    {resultado.categoria}")
        print(f"Justificación:{resultado.justificacion}")
        print("-" * 60)


if __name__ == "__main__":
    main()
