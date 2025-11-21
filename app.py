import streamlit as st
from openai import OpenAI
import requests
import os
import pygame
from io import BytesIO
from gtts import gTTS  # <--- AGREGA ESTO

# --- CONFIGURACIÓN INICIAL DE STREAMLIT ---
st.set_page_config(
    page_title="Narrador de Pesadillas",
    page_icon="👻",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# CSS Personalizado para estilo terror
st.markdown("""
<style>
    .main { background-color: #0e0e0e; color: #d4d4d4; }
    .stTextInput > div > div > input { background-color: #1f1f1f; color: #ff4b4b; border-color: #ff4b4b; }
    .stButton > button { background-color: #5a0000; color: white; border-radius: 5px; border: 1px solid #ff0000; }
    .stButton > button:hover { background-color: #8a0000; border-color: #ffffff; }
    h1, h2, h3 { color: #ff3333 !important; font-family: 'Courier New', monospace; }
    .story-text {
        font-family: 'Georgia', serif; font-size: 18px; line-height: 1.6;
        color: #e0e0e0; background-color: #1a1a1a; padding: 20px;
        border-left: 5px solid #800000; margin-top: 20px; border-radius: 5px;
    }
    .flicker-text { animation: flicker 4s infinite; color: #ff0000; text-align: center; }
    @keyframes flicker {
        0%, 100% { opacity: 1; } 50% { opacity: 0.8; } 52% { opacity: 0.2; } 54% { opacity: 0.8; }
    }
</style>
""", unsafe_allow_html=True)

# --- INICIALIZACIÓN DE AUDIO ---
try:
    pygame.mixer.init()
except Exception as e:
    st.warning("No se pudo inicializar el sistema de audio. (Puede fallar en servidores cloud).")

# --- FUNCIONES DEL NUCLEO (GROQ + HUGGING FACE) ---

def generate_horror_content(prompt_palabra, max_tokens=800):
    """
   conexion a la API de Groq con fines de generacion de historias.
    """
    try:
        client = OpenAI(
            api_key=st.secrets[""],
            base_url="",
        )

        system_prompt = """
Eres un director de cine de terror experto.
1. HISTORIA: Corta y aterradora en español.
2. IMAGEN: Descripción visual en inglés.
3. MUSICA: Solo una palabra: SUSPENSO, ACCION, o SOBRENATURAL.

FORMATO:
[HISTORIA]
...texto...
[IMAGEN]
...texto...
[MUSICA]
...palabra...
"""
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Palabra clave: '{prompt_palabra}'"}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.75,
            max_tokens=max_tokens,
        )

        full_text = chat_completion.choices[0].message.content

        # Valores por defecto
        story = "Error al procesar la historia."
        img_prompt = ""
        mood = "SUSPENSO" # Por defecto

        if "[HISTORIA]" in full_text:
            parts = full_text.split("[IMAGEN]")
            story = parts[0].replace("[HISTORIA]", "").strip()
            
            if len(parts) > 1:
                remaining = parts[1]
                if "[MUSICA]" in remaining:
                    img_parts = remaining.split("[MUSICA]")
                    img_prompt = img_parts[0].strip()
                    
                    # --- CORRECCIÓN APLICADA AQUÍ ---
                    raw_mood = img_parts[1].strip().upper()
                    
                    # Buscamos la palabra clave dentro del texto sucio
                    if "ACCION" in raw_mood or "ACCIÓN" in raw_mood:
                        mood = "ACCION"
                    elif "SOBRENATURAL" in raw_mood:
                        mood = "SOBRENATURAL"
                    else:
                        mood = "SUSPENSO"
        
        return story, img_prompt, mood

    except Exception as e:
        st.error(f"Error crítico en Groq: {e}")
        return None, None, None
    
def narrate_story(text):
    """Genera el audio solo cuando se solicita"""
    try:
        if not os.path.exists("audio"):
            os.makedirs("audio")
        
        file_path = "audio/narration.mp3"
        tts = gTTS(text=text, lang='es')
        tts.save(file_path)
        return file_path
    except Exception as e:
        st.error(f"Error al crear la voz: {e}")
        return None
