#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agente Smith - Main Entry Point

Arquivo principal para inicializar e executar o Agente Smith.
Week 1: MVP com voz, WhatsApp e controle de aplicativos Android.
"""

import sys
import logging
import argparse
from typing import Optional

# Imports dos modulos principais
from adb_bridge import ADBBridge
from voice_controller import VoiceController
from whatsapp_handler import WhatsAppHandler
from security_manager import SecurityManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AgenteSmith:
    """Classe principal do Agente Smith."""
    
    def __init__(self, config: Optional[dict] = None):
        """Inicializa o Agente Smith.
        
        Args:
            config: Dicionario com configuracoes customizadas
        """
        self.config = config or {}
        self.adb = None
        self.voice = None
        self.whatsapp = None
        self.security = None
        self.running = False
        
    def initialize(self) -> bool:
        """Inicializa todos os componentes do agente.
        
        Returns:
            bool: True se inicializacao bem-sucedida
        """
        try:
            logger.info("Inicializando Agente Smith...")
            
            # Inicializa gerenciador de seguranca
            admin_key = self.config.get('admin_key', 'default_key')
            self.security = SecurityManager(admin_key)
            logger.info("Gerenciador de seguranca inicializado")
            
            # Inicializa bridge ADB
            device_id = self.config.get('device_id', None)
            self.adb = ADBBridge(device_id=device_id)
            if self.adb.connect():
                logger.info("ADB Bridge conectado")
            else:
                logger.warning("Falha ao conectar ADB")
            
            # Inicializa controlador de voz
            language = self.config.get('language', 'pt-BR')
            self.voice = VoiceController(language=language)
            if self.voice.initialize():
                logger.info("Controlador de voz inicializado")
            else:
                logger.warning("Falha ao inicializar voz")
            
            # Inicializa handler do WhatsApp
            phone = self.config.get('phone_number', '')
            self.whatsapp = WhatsAppHandler(
                phone_number=phone,
                chrome_profile_path=self.config.get('chrome_profile', '')
            )
            if self.whatsapp.initialize_whatsapp():
                logger.info("WhatsApp conectado")
            else:
                logger.warning("Falha ao conectar WhatsApp")
            
            logger.info("Agente Smith inicializado com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro durante inicializacao: {str(e)}")
            return False
    
    def run(self) -> None:
        """Inicia o loop principal do agente."""
        if not self.initialize():
            logger.error("Nao foi possivel inicializar o agente")
            return
        
        self.running = True
        logger.info("Agente Smith em execucao. Pressione Ctrl+C para parar.")
        
        try:
            while self.running:
                # Loop principal - aguarda comandos
                # TODO: Implementar loop de eventos
                pass
        except KeyboardInterrupt:
            logger.info("Parando Agente Smith...")
        finally:
            self.shutdown()
    
    def shutdown(self) -> None:
        """Encerra o agente e libera recursos."""
        try:
            logger.info("Encerrando Agente Smith...")
            
            if self.whatsapp:
                self.whatsapp.close()
            if self.voice:
                self.voice.close()
            if self.adb:
                self.adb.disconnect()
            
            self.running = False
            logger.info("Agente Smith encerrado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao encerrar: {str(e)}")

def main():
    """Funcao principal para executar o Agente Smith."""
    parser = argparse.ArgumentParser(
        description='Agente Smith - Android Intelligent Agent'
    )
    parser.add_argument(
        '--device-id',
        help='ID do dispositivo Android',
        default=None
    )
    parser.add_argument(
        '--language',
        help='Idioma para reconhecimento de voz',
        default='pt-BR'
    )
    parser.add_argument(
        '--config',
        help='Arquivo de configuracao (JSON)',
        default=None
    )
    
    args = parser.parse_args()
    
    # Prepara configuracoes
    config = {
        'device_id': args.device_id,
        'language': args.language,
    }
    
    # Inicia agente
    agent = AgenteSmith(config=config)
    agent.run()

if __name__ == '__main__':
    main()
