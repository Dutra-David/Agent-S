#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NLP Command Bridge - Integração entre NLP Processor e Command Parser
Week 2: Integrando processamento de linguagem natural com parsing de comandos
"""

import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime

from nlp_processor import NLPProcessor, SentenceEmbedding
from command_parser import CommandParser, ParsedCommand, CommandType
from ml_enhanced_nlp import MLEnhancedNLP, MLEnhancedResult
import time

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ProcessedCommand:
    """Representa um comando processado pelo NLP."""
    original_input: str
    parsed_command: Optional[ParsedCommand]
    nlp_confidence: float
    command_confidence: float
    semantic_meaning: str
    timestamp: datetime
    
    @property
    def combined_confidence(self) -> float:
        """Calcula confiança combinada NLP + Parser."""
        return (self.nlp_confidence + self.command_confidence) / 2


class NLPCommandBridge:
    """
    Bridge entre NLP Processor e Command Parser.
    Combina análise semântica com parsing estruturado de comandos.
    """
    
    def __init__(self, min_nlp_confidence: float = 0.7, 
                 min_parser_confidence: float = 0.8):
        """
        Inicializa o bridge.
        
        Args:
            min_nlp_confidence: Confiança mínima do NLP (0-1)
            min_parser_confidence: Confiança mínima do Parser (0-1)
        """
        self.nlp = NLPProcessor()
        self.parser = CommandParser()
        self.min_nlp_confidence = min_nlp_confidence
        self.min_parser_confidence = min_parser_confidence
        self.processing_history: List[ProcessedCommand] = []
        self.command_confidence_cache: Dict[str, float] = {}
        
        logger.info("NLP Command Bridge inicializado")
    
    def process_input(self, user_input: str, use_nlp_fallback: bool = True) -> Optional[ProcessedCommand]:
        """
        Processa entrada do usuário usando NLP + Parser.
        
        Args:
            user_input: Texto de entrada do usuário
            use_nlp_fallback: Usar NLP se parser falhar
            
        Returns:
            ProcessedCommand ou None se não conseguir processar
        """
        if not user_input or not user_input.strip():
            logger.warning("Entrada vazia recebida")
            return None
        
        try:
            # Processa com NLP
            nlp_result = self.nlp.analyze_text(user_input)
            nlp_confidence = nlp_result.get('confidence', 0.0) if nlp_result else 0.0
            semantic_meaning = nlp_result.get('semantic_meaning', '') if nlp_result else ''
            
            # Tenta fazer parse com o parser
            parsed_command = self.parser.parse(user_input)
            parser_confidence = parsed_command.confidence if parsed_command else 0.0
            
            # Se parser falhou, tenta extrair comando do NLP
            if parsed_command is None and use_nlp_fallback and nlp_result:
                parsed_command = self._extract_command_from_nlp(nlp_result, user_input)
                if parsed_command:
                    parser_confidence = nlp_confidence * 0.8  # Reduz confiança do fallback
            
            # Validação de confiança
            if nlp_confidence < self.min_nlp_confidence:
                logger.warning(f"Confiança NLP baixa: {nlp_confidence:.2f}")
            
            if parsed_command and parser_confidence < self.min_parser_confidence:
                logger.warning(f"Confiança do Parser baixa: {parser_confidence:.2f}")
            
            # Cria comando processado
            processed = ProcessedCommand(
                original_input=user_input,
                parsed_command=parsed_command,
                nlp_confidence=nlp_confidence,
                command_confidence=parser_confidence,
                semantic_meaning=semantic_meaning,
                timestamp=datetime.now()
            )
            
            self.processing_history.append(processed)
            logger.info(f"Input processado com confiança combinada: {processed.combined_confidence:.2f}")
            
            return processed
            
        except Exception as e:
            logger.error(f"Erro ao processar input: {str(e)}")
            return None
    
    def _extract_command_from_nlp(self, nlp_result: Dict[str, Any], 
                                  user_input: str) -> Optional[ParsedCommand]:
        """
        Extrai comando estruturado a partir dos resultados do NLP.
        
        Args:
            nlp_result: Resultado da análise NLP
            user_input: Texto original
            
        Returns:
            ParsedCommand ou None
        """
        try:
            # Mapeamento de tipos semânticos para tipos de comando
            semantic_to_command_type = {
                'open_app': CommandType.OPEN_APP,
                'close_app': CommandType.CLOSE_APP,
                'message': CommandType.SEND_MESSAGE,
                'call': CommandType.CALL,
                'url': CommandType.OPEN_URL,
                'screenshot': CommandType.TAKE_SCREENSHOT,
            }
            
            semantic = nlp_result.get('semantic_meaning', '').lower()
            cmd_type = None
            
            for key, cmd in semantic_to_command_type.items():
                if key in semantic:
                    cmd_type = cmd
                    break
            
            if cmd_type is None:
                cmd_type = CommandType.GENERIC
            
            # Cria comando a partir do NLP
            parsed_cmd = ParsedCommand(
                command_type=cmd_type,
                action=cmd_type.value,
                parameters=nlp_result.get('entities', {}),
                confidence=nlp_result.get('confidence', 0.0) * 0.8,
                raw_input=user_input
            )
            
            return parsed_cmd
            
        except Exception as e:
            logger.error(f"Erro ao extrair comando do NLP: {str(e)}")
            return None
    
    def get_processing_history(self, limit: Optional[int] = None) -> List[ProcessedCommand]:
        """
        Retorna histórico de processamentos.
        
        Args:
            limit: Limitar número de resultados
            
        Returns:
            Lista de ProcessedCommand
        """
        if limit:
            return self.processing_history[-limit:]
        return self.processing_history
    
    def clear_history(self) -> None:
        """
        Limpa o histórico de processamentos.
        """
        self.processing_history.clear()
        logger.info("Histórico de processamentos limpo")
    
    def evaluate_performance(self) -> Dict[str, Any]:
        """
        Avalia o desempenho do bridge.
        
        Returns:
            Dicionário com métricas de desempenho
        """
        if not self.processing_history:
            return {'error': 'Sem histórico de processamentos'}
        
        total = len(self.processing_history)
        successful = sum(1 for p in self.processing_history if p.parsed_command is not None)
        avg_confidence = sum(p.combined_confidence for p in self.processing_history) / total if total > 0 else 0
        
        return {
            'total_processed': total,
            'successful_commands': successful,
            'success_rate': (successful / total * 100) if total > 0 else 0,
            'average_confidence': avg_confidence,
            'high_confidence_commands': sum(1 for p in self.processing_history 
                                           if p.combined_confidence >= 0.9)
        }


def demo():
    """
    Demonstração do NLP Command Bridge.
    """
    logger.info("Iniciando demonstração do NLP Command Bridge...")
    
    bridge = NLPCommandBridge()
    
    test_inputs = [
        "Abre o WhatsApp",
        "Manda uma mensagem para João dizendo oi",
        "Fecha o Facebook",
        "Liga para Maria",
        "Abre o Google",
        "Captura de tela",
    ]
    
    for test_input in test_inputs:
        logger.info(f"\nProcessando: '{test_input}'")
        result = bridge.process_input(test_input)
        
        if result:
            if result.parsed_command:
                logger.info(f"Comando: {result.parsed_command.action}")
                logger.info(f"Parâmetros: {result.parsed_command.parameters}")
            logger.info(f"Confiança combinada: {result.combined_confidence:.2f}")
    
    # Relatório de desempenho
    logger.info("\n--- Relatório de Desempenho ---")
    metrics = bridge.evaluate_performance()
    for key, value in metrics.items():
        logger.info(f"{key}: {value}")


if __name__ == '__main__':
    demo()
