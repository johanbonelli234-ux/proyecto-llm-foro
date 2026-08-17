from layer1_io import cargar_mensajes
from layer2_llm import clasificar_mensaje

def ejecutar_cli():
    print("==========================================")
    print("      SISTEMA DE ANÁLISIS DE FOROS        ")
    print("==========================================\n")

    # 1. Ejecutar Capa 1
    print("[Capa 1] Cargando datos desde el archivo...")
    mensajes = cargar_mensajes("foro_datos.txt")
    
    if not mensajes:
        print("No se pudieron cargar mensajes. Revisa el archivo datos.")
        return

    print(f"✓ Se cargaron {len(mensajes)} mensajes correctamente.\n")

    # 2. Ejecutar Capa 2 y Capa 3
    print("[Capa 2 & 3] Clasificando intervenciones con Gemini LLM...\n")
    print("-" * 60)
    print(f"{'USUARIO':<12} | {'CATEGORÍA':<15} | {'MENSAJE'}")
    print("-" * 60)

    for m in mensajes:
        categoria = clasificar_mensaje(m["mensaje"])
        print(f"{m['usuario']:<12} | {categoria.upper():<15} | {m['mensaje']}")

    print("-" * 60)
    print("\n¡Proceso completado exitosamente!")

if __name__ == "__main__":
    ejecutar_cli()