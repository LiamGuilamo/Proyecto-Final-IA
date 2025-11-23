import os
import subprocess
import sys


def check_dependencies():
    """Verificar si todas las dependencias requeridas están instaladas"""
    try:
        import streamlit as st
        import pygame
        import gtts
        import openai
        import requests
        print("✅ Todas las dependencias requeridas están instaladas.") 
        return True
    except ImportError as e:
        print(f"❌ Dependencia faltante: {e}")
        print("Instalando dependencias...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("✅ Dependencias instaladas exitosamente.")
            return True
        except subprocess.CalledProcessError:
            print("❌ Error al instalar dependencias. Por favor, ejecuta 'pip install -r requirements.txt' manualmente.")
            return False


def run_app():
    """Ejecutar la aplicación Streamlit"""
    print("Iniciando Narrador de Historias de Terror...")
    subprocess.call(["streamlit", "run", "app.py"])

if __name__ == "__main__":
    print("🔥👻 Narrador de Historias de Terror con IA ⚰️🔥")
    print("=======================================")
    
    if check_dependencies():
    
        run_app()
    else:
        print("Por favor, soluciona los problemas de dependencias e inténtalo de nuevo.") 