import streamlit as st
from openai import OpenAI
import requests
import os
import pygame
from io import BytesIO
from gtts import gTTS 

# CONFIGURACIÓN INICIAL DE STREAMLIT 
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

#INICIALIZACIÓN DE AUDIO
try:
    pygame.mixer.init()
except Exception as e:
    st.warning("No se pudo inicializar el sistema de audio. (Puede fallar en servidores cloud).")

# FUNCIONES DEL NUCLEO (GROQ )

def generate_horror_content(prompt_palabra, max_tokens=800):
    """
   conexion a la API de Groq con fines de generacion de historias.
    """
    try:
        client = OpenAI(
            api_key=st.secrets["GROQ_API_KEY"],
            base_url="https://api.groq.com/openai/v1",
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
    
def generate_image_hf(image_prompt):
    """
    Genera imágenes usando la API pública y gratuita de Pollinations.ai.
    """
    try:
        # Pollinations permite personalizar el modelo añadiendo parámetros a la URL
        # model='flux' da resultados muy realistas y de terror (mejores que SD 1.5)
        prompt_encoded = requests.utils.quote(image_prompt)
        
        # URL Mágica: simplemente pones el prompt en la URL
        api_url = f"https://image.pollinations.ai/prompt/{prompt_encoded}?model=flux&width=1024&height=768&nologo=true"
        
        st.info(f"🎨 Generando arte con Pollinations...")
        
        # Hacemos la petición 
        response = requests.get(api_url)
        
        if response.status_code == 200:
            st.success("✅ Imagen manifestada con éxito.")
            return BytesIO(response.content)
        else:
            st.error(f"❌ Error en la invocación visual: {response.status_code}")
            return None
            
    except Exception as e:
        st.error(f"❌ Algo salió mal en el ritual de imagen: {e}")
        return None

def play_music(mood):
    """Gestiona la reproducción de música según el ambiente"""
    # Funcion para reproducir la musica, dependiendo del tipo de escenario
    music_map = {
        "SUSPENSO": "music/suspense.mp3",
        "ACCION": "music/action.mp3",
        "SOBRENATURAL": "music/creepy.mp3"
    }
    
    file_path = music_map.get(mood, "music/suspense.mp3")
    
    if not os.path.exists("music"):
        os.makedirs("music") # Crea la carpeta si no existe
        
    if os.path.exists(file_path):
        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play(-1) # Loop infinito
            pygame.mixer.music.set_volume(0.4)
        except Exception as e:
            st.warning(f"Error reproduciendo audio: {e}")
    else:
        
        pass


def stop_music():
    try:
        pygame.mixer.music.stop()
    except:
        pass

# --- INTERFAZ PRINCIPAL ---

def main():
    st.markdown("<h1 class='flicker-text'>💀 NARRADOR DE PESADILLAS 💀</h1>", unsafe_allow_html=True)
    st.markdown("---")
    
    # GESTIÓN DE ESTADO 
    # Inicializamos variables para que no se borren al dar clic en botones
    if 'current_story' not in st.session_state:
        st.session_state['current_story'] = None
    if 'current_mood' not in st.session_state:
        st.session_state['current_mood'] = None
    if 'current_image' not in st.session_state:
        st.session_state['current_image'] = None
    if 'img_prompt' not in st.session_state:
        st.session_state['img_prompt'] = ""

    # BARRA DE ENTRADA 
    col1, col2 = st.columns([3, 1])
    with col1:
        input_word = st.text_input("¿Qué alimenta tu miedo hoy?", placeholder="Ej: Espejo, Sótano, Muñeca...")
    with col2:
        st.write("") 
        st.write("")
        if st.button("⛔ SILENCIO"):
            stop_music()

     # BOTÓN DE GENERACIÓN (INVOCAR)
    if st.button("🔮 INVOCAR HISTORIA", use_container_width=True):
        if not input_word:
            st.warning("Debes ofrecer una palabra para el ritual...")
        else:
            with st.status("Realizando ritual de invocación...", expanded=True) as status:
                
                # 1. Generar Texto (Groq)
                st.write("🧠 Consultando a los espíritus...")
                story, img_prompt, mood = generate_horror_content(input_word)
                
                if story:
                    # Guardamos todo en session_state
                    st.session_state['current_story'] = story
                    st.session_state['current_mood'] = mood
                    st.session_state['img_prompt'] = img_prompt
                    
                    # 2. Generar Imagen
                    st.write("🎨 Materializando la visión...")
                    image_data = generate_image_hf(img_prompt) 
                    st.session_state['current_image'] = image_data
                    
                    # 3. Audio de Fondo
                    st.write(f"🎵 Sintonizando ambiente: {mood}...")
                    play_music(mood)
                    
                    status.update(label="¡El ritual se ha completado!", state="complete", expanded=False)
                else:
                    status.update(label="El ritual falló.", state="error")

    # MOSTRAR RESULTADOS (ESTO SE EJECUTA SIEMPRE QUE HAYA HISTORIA) 
    if st.session_state['current_story']:
        st.markdown("---")
        
        c_img, c_txt = st.columns([1, 1.5])
        
        with c_img:
            if st.session_state['current_image']:
                st.image(st.session_state['current_image'], 
                         caption=f"Vision: {st.session_state['img_prompt'][:30]}...", 
                         use_container_width=True)
            else:
                st.warning("La imagen no pudo manifestarse.")
                
        with c_txt:
            mood = st.session_state['current_mood']
            st.markdown(f"### Ambiente Detectado: *{mood}*")
            
            # BOTÓN DE NARRAR 
            # Usamos una key única para evitar conflictos
            if st.button("🗣️ NARRAR HISTORIA EN VOZ ALTA", key="btn_narrar"):
                with st.spinner("Invocando la voz de ultratumba..."):
                    audio_file = narrate_story(st.session_state['current_story'])
                    if audio_file:
                        # Autoplay=True hace que suene apenas termina de cargar
                        st.audio(audio_file, format="audio/mp3", start_time=0, autoplay=True)

            # Texto de la historia
            st.markdown(f'<div class="story-text">{st.session_state["current_story"]}</div>', unsafe_allow_html=True)
if __name__ == "__main__":
    main()

