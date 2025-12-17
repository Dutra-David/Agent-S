#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Voice NLP Integration - Integração entre Voice Controller e NLP
Week 3: Pipeline de aáudio -> texto -> comando
"""

import logging
from typing import Optional, Callable, Dict, Any
from dataclasses import dataclass
from datetime import datetime
from threading import Thread
import queue

from advanced_logger import get_logger, LogLevel
from nlp_command_bridge import NLPCommandBridge, ProcessedCommand

logger = get_logger("voice_nlp_integration", log_level=LogLevel.INFO)


@dataclass
class VoiceInput:
    """Representa um input de áudio."""
    audio_data: bytes
    confidence: float
    language: str
    timestamp: datetime


@dataclass
class TranscribedText:
    """Texto transcrito do áudio."""
    text: str
    confidence: float
    language: str
    timestamp: datetime


class VoiceNLPIntegration:
    """
    Integra Voice Input com NLP Processing.
    Pipeline: Aáudio -> Transcrição -> NLP -> Comando
    """
    
    def __init__(self, language: str = "pt-BR"):
        """
        Inicializa a integração.
        
        Args:
            language: Idioma padrão (pt-BR)
        """
        self.language = language
        self.nlp_bridge = NLPCommandBridge()
        self.transcription_service = None
        self.text_queue: queue.Queue = queue.Queue()
        self.command_queue: queue.Queue = queue.Queue()
        self.running = False
        
        logger.info(f"Voice NLP Integration inicializado com idioma: {language}")
    
    def set_transcription_service(self, service: Callable) -> None:
        """
        Define o serviço de transcrição (ex: Google Speech-to-Text, Whisper).
        
        Args:
            service: Função que converte áudio para texto
        """
        self.transcription_service = service
        logger.info("Serviço de transcrição definido")
    
    def transcribe_audio(self, voice_input: VoiceInput) -> Optional[TranscribedText]:
        """
        Transcreve áudio para texto.
        
        Args:
            voice_input: Dados de áudio
            
        Returns:
            Texto transcrito ou None
        """
        if not self.transcription_service:
            logger.error("Serviço de transcrição não definido")
            return None
        
        try:
            text = self.transcription_service(voice_input.audio_data, self.language)
            
            transcribed = TranscribedText(
                text=text,
                confidence=voice_input.confidence,
                language=voice_input.language,
                timestamp=datetime.now()
            )
            
            logger.info(f"Áudio transcrito: '{text}'")
            return transcribed
            
        except Exception as e:
            logger.error(f"Erro na transcrição: {e}", exception=e)
            return None
    
    def process_voice_input(self, voice_input: VoiceInput) -> Optional[ProcessedCommand]:
        """
        Processa input de voz completo: áudio -> texto -> comando.
        
        Args:
            voice_input: Dados de áudio
            
        Returns:
            Comando processado ou None
        """
        # 1. Transcrever aáudio
        transcribed = self.transcribe_audio(voice_input)
        if not transcribed:
            logger.warning("Falha na transcrição de áudio")
            return None
        
        # 2. Processar com NLP
        processed_command = self.nlp_bridge.process_input(transcribed.text)
        if not processed_command:
            logger.warning(f"Falha ao processar comando de voz: {transcribed.text}")
            return None
        
        logger.info(
            f"Comando de voz processado com sucesso. "
            f"Confiança: {processed_command.combined_confidence:.2f}"
        )
        
        self.command_queue.put(processed_command)
        return processed_command
    
    def start_listening(self) -> None:
        """
        Inicia thread de escuta de entrada de voz.
        """
        if self.running:
            logger.warning("Ja está escutando")
            return
        
        self.running = True
        thread = Thread(target=self._listening_loop, daemon=True)
        thread.start()
        logger.info("Iniciado listener de voz")
    
    def _listening_loop(self) -> None:
        """
        Loop de escuta contínua.
        """
        logger.debug("Iniciando loop de escuta")
        while self.running:
            try:
                # Aguarda input de voz (simulado)
                pass
            except Exception as e:
                logger.error(f"Erro no loop de escuta: {e}", exception=e)
    
    def stop_listening(self) -> None:
        """
        Para a escuta de voz.
        """
        self.running = False
        logger.info("Listener de voz parado")
    
    def get_next_command(self, timeout: int = 5) -> Optional[ProcessedCommand]:
        """
        Obtém próximo comando processado da fila.
        
        Args:
            timeout: Timeout em segundos
            
        Returns:
            Próximo comando ou None
        """
        try:
            return self.command_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def get_integration_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas da integração.
        
        Returns:
            Dict com estáticas
        """
        nlp_metrics = self.nlp_bridge.evaluate_performance()
        
        return {
            'language': self.language,
            'nlp_metrics': nlp_metrics,
            'commands_in_queue': self.command_queue.qsize(),
            'running': self.running
        }


if __name__ == "__main__":
    # Demo
    integration = VoiceNLPIntegration(language="pt-BR")
    
    # Simulação de transcrição
    def mock_transcription(audio, language):
        return "Abre o WhatsApp"
    
    integration.set_transcription_service(mock_transcription)
    
    # Simulação de input de voz
    voice_input = VoiceInput(
        audio_data=b"audio_data_simulado",
        confidence=0.95,
        language="pt-BR",
        timestamp=datetime.now()
    )
    
    command = integration.process_voice_input(voice_input)
    if command:
        print(f"Comando processado: {command.parsed_command.action}")
