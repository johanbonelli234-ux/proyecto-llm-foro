import os
import google.generativeai as genai

API_KEY = "TU_API_KEY_AQUI"

genai.configure(api_key=API_KEY)

def clasificar_mensaje(mensaje_texto):
    """
    Capa 2: Envía el mensaje a Gemini y retorna la categoría.
    """
    model = genai.GenerativeModel("gemini-2.5-flash")
    
    prompt = f"""
    Actúa como un clasificador de mensajes de foros educativos.
    Clasifica el siguiente mensaje en exactamente una de estas opciones:
    [pregunta, respuesta, off-topic, retroalimentacion].
    
    Mensaje: "{mensaje_texto}"
    
    Responde ÚNICAMENTE con la categoría (una sola palabra).
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip().lower()
    except Exception as e:
        return "error"