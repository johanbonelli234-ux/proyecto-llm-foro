import os

def cargar_mensajes(ruta_archivo="foro_datos.txt"):
    """
    Capa 1: Lee el archivo de datos y devuelve una lista de mensajes.
    """
    if not os.path.exists(ruta_archivo):
        print(f"❌ Error: El archivo '{ruta_archivo}' no existe.")
        return []

    mensajes = []
    with open(ruta_archivo, 'r', encoding='utf-8') as f:
        for linea in f:
            linea = linea.strip()
            if linea and ',' in linea:
                partes = linea.split(',', 2)
                if len(partes) == 3:
                    usuario, fecha, texto = partes
                    mensajes.append({
                        "usuario": usuario.strip(),
                        "fecha": fecha.strip(),
                        "mensaje": texto.strip()
                    })
    return mensajes