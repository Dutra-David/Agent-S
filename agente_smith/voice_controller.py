"""Voice Controller - Reconhecimento de voz e Text-to-Speech (#1)"""

import speech_recognition as sr
import pyttsx3
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class VoiceController:
    """Controla Agent-S via voz - #1 Melhoria"""
    
    def __init__(self, language='pt-BR'):
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()
        self.language = language
        self.engine.setProperty('rate', 150)
        self.engine.setProperty('volume', 0.9)
        logger.info("Voice Controller inicializado")
    
    def speak(self, text: str):
        """Faz o Agent falar"""
        try:
            logger.info(f"Falando: {text}")
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            logger.error(f"Erro ao falar: {e}")
    
    def listen(self, timeout: int = 10) -> Optional[str]:
        """Escuta comando de voz"""
        try:
            logger.info("Escutando...")
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=timeout)
            
            # Usa Google Speech Recognition
            text = self.recognizer.recognize_google(audio, language=self.language)
            logger.info(f"Reconhecido: {text}")
            return text
        
        except sr.UnknownValueError:
            msg = "N\u00e3o entendi. Tenta novamente!"
            self.speak(msg)
            return None
        except sr.RequestError as e:
            msg = f"Erro de conex\u00e3o: {e}"
            self.speak(msg)
            logger.error(msg)
            return None
    
    def confirm_action(self, action: str) -> bool:
        """Pede confirma\u00e7\u00e3o de voz"""
        msg = f"Vou {action}. Confirmar?"
        self.speak(msg)
        response = self.listen(timeout=5)
        
        if response:
            if 'sim' in response.lower() or 'yes' in response.lower():
                self.speak("Confirmado!")
                return True
            else:
                self.speak("Cancelado!")
                return False
        return False
