"""Agente Smith - Android Intelligent Agent

Python package para o Agente Smith inteligente para Android.
Week 1: MVP principal com voz, WhatsApp e controle de aplicativos.
"""

__version__ = "0.1.0"
__author__ = "Dutra-David"
__description__ = "Android Intelligent Agent with Voice, WhatsApp and App Control"

from .adb_bridge import ADBBridge
from .voice_controller import VoiceController
from .whatsapp_handler import WhatsAppHandler
from .security_manager import SecurityManager

__all__ = [
    'ADBBridge',
    'VoiceController', 
    'WhatsAppHandler',
    'SecurityManager',
]

# Configuracoes padrao
DEFAULT_CONFIG = {
    'device_port': 5037,
    'voice_model': 'pt-BR',
    'security_level': 'media',
    'session_timeout': 3600,
}
