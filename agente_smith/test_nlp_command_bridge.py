#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Testes Unitários para NLP Command Bridge
Week 2: Testes de integração NLP + Command Parser
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from nlp_command_bridge import NLPCommandBridge, ProcessedCommand
from command_parser import CommandType, ParsedCommand


class TestProcessedCommand(unittest.TestCase):
    """Testes para a classe ProcessedCommand."""
    
    def setUp(self):
        """Configura os testes."""
        self.parsed_cmd = ParsedCommand(
            command_type=CommandType.OPEN_APP,
            action="open_app",
            parameters={"app_name": "WhatsApp"},
            confidence=0.9,
            raw_input="Abre o WhatsApp"
        )
    
    def test_processed_command_creation(self):
        """Testa criação de ProcessedCommand."""
        processed = ProcessedCommand(
            original_input="Abre o WhatsApp",
            parsed_command=self.parsed_cmd,
            nlp_confidence=0.85,
            command_confidence=0.9,
            semantic_meaning="open_app",
            timestamp=datetime.now()
        )
        
        self.assertEqual(processed.original_input, "Abre o WhatsApp")
        self.assertIsNotNone(processed.parsed_command)
        self.assertEqual(processed.semantic_meaning, "open_app")
    
    def test_combined_confidence_calculation(self):
        """Testa cálculo de confiança combinada."""
        processed = ProcessedCommand(
            original_input="Abre o WhatsApp",
            parsed_command=self.parsed_cmd,
            nlp_confidence=0.8,
            command_confidence=0.9,
            semantic_meaning="open_app",
            timestamp=datetime.now()
        )
        
        expected_confidence = (0.8 + 0.9) / 2
        self.assertEqual(processed.combined_confidence, expected_confidence)


class TestNLPCommandBridge(unittest.TestCase):
    """Testes para a classe NLPCommandBridge."""
    
    def setUp(self):
        """Configura os testes."""
        with patch('nlp_command_bridge.NLPProcessor'):
            with patch('nlp_command_bridge.CommandParser'):
                self.bridge = NLPCommandBridge()
    
    def test_bridge_initialization(self):
        """Testa inicialização do bridge."""
        self.assertIsNotNone(self.bridge.nlp)
        self.assertIsNotNone(self.bridge.parser)
        self.assertEqual(self.bridge.min_nlp_confidence, 0.7)
        self.assertEqual(self.bridge.min_parser_confidence, 0.8)
    
    def test_empty_input_processing(self):
        """Testa processamento de entrada vazia."""
        result = self.bridge.process_input("")
        self.assertIsNone(result)
        
        result = self.bridge.process_input("   ")
        self.assertIsNone(result)
    
    @patch('nlp_command_bridge.NLPProcessor.analyze_text')
    @patch('nlp_command_bridge.CommandParser.parse')
    def test_successful_command_parsing(self, mock_parser, mock_nlp):
        """Testa parsing bem-sucedido de comando."""
        # Configura mocks
        mock_nlp.return_value = {
            'confidence': 0.85,
            'semantic_meaning': 'open_app',
            'entities': {'app_name': 'WhatsApp'}
        }
        
        mock_parser.return_value = ParsedCommand(
            command_type=CommandType.OPEN_APP,
            action="open_app",
            parameters={"app_name": "WhatsApp"},
            confidence=0.9,
            raw_input="Abre o WhatsApp"
        )
        
        # Processa input
        result = self.bridge.process_input("Abre o WhatsApp")
        
        # Verificações
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.parsed_command)
        self.assertEqual(result.parsed_command.action, "open_app")
        self.assertEqual(len(self.bridge.processing_history), 1)
    
    @patch('nlp_command_bridge.NLPProcessor.analyze_text')
    @patch('nlp_command_bridge.CommandParser.parse')
    def test_nlp_fallback(self, mock_parser, mock_nlp):
        """Testa fallback para NLP quando parser falha."""
        # Configura mocks
        mock_nlp.return_value = {
            'confidence': 0.85,
            'semantic_meaning': 'open_app',
            'entities': {'app_name': 'WhatsApp'}
        }
        
        mock_parser.return_value = None  # Parser falha
        
        # Processa input
        result = self.bridge.process_input("Abre o WhatsApp", use_nlp_fallback=True)
        
        # Verificações
        self.assertIsNotNone(result)
        # Com fallback, deve extrair comando do NLP
        if result.parsed_command:
            self.assertIsNotNone(result.parsed_command.action)
    
    def test_processing_history(self):
        """Testa histórico de processamentos."""
        # Verifica histórico vazio
        self.assertEqual(len(self.bridge.processing_history), 0)
        
        # Adiciona alguns processamentos
        processed1 = ProcessedCommand(
            original_input="Teste 1",
            parsed_command=None,
            nlp_confidence=0.8,
            command_confidence=0.0,
            semantic_meaning="",
            timestamp=datetime.now()
        )
        self.bridge.processing_history.append(processed1)
        
        self.assertEqual(len(self.bridge.processing_history), 1)
    
    def test_clear_history(self):
        """Testa limpeza do histórico."""
        # Adiciona um processamento
        processed = ProcessedCommand(
            original_input="Teste",
            parsed_command=None,
            nlp_confidence=0.8,
            command_confidence=0.0,
            semantic_meaning="",
            timestamp=datetime.now()
        )
        self.bridge.processing_history.append(processed)
        
        # Verifica que tem um item
        self.assertEqual(len(self.bridge.processing_history), 1)
        
        # Limpa
        self.bridge.clear_history()
        
        # Verifica que está vazio
        self.assertEqual(len(self.bridge.processing_history), 0)
    
    def test_evaluate_performance_empty(self):
        """Testa avaliação de desempenho com histórico vazio."""
        metrics = self.bridge.evaluate_performance()
        self.assertIn('error', metrics)
    
    def test_evaluate_performance_with_data(self):
        """Testa avaliação de desempenho com dados."""
        # Adiciona alguns processamentos
        for i in range(3):
            processed = ProcessedCommand(
                original_input=f"Teste {i}",
                parsed_command=self.parsed_cmd if i < 2 else None,
                nlp_confidence=0.8 + (i * 0.05),
                command_confidence=0.85 + (i * 0.05),
                semantic_meaning="test",
                timestamp=datetime.now()
            )
            self.bridge.processing_history.append(processed)
        
        metrics = self.bridge.evaluate_performance()
        
        self.assertEqual(metrics['total_processed'], 3)
        self.assertEqual(metrics['successful_commands'], 2)
        self.assertGreater(metrics['average_confidence'], 0)


class TestCommandExtraction(unittest.TestCase):
    """Testes para extração de comandos a partir de NLP."""
    
    def setUp(self):
        """Configura os testes."""
        with patch('nlp_command_bridge.NLPProcessor'):
            with patch('nlp_command_bridge.CommandParser'):
                self.bridge = NLPCommandBridge()
    
    def test_extract_command_open_app(self):
        """Testa extração de comando para abrir app."""
        nlp_result = {
            'confidence': 0.85,
            'semantic_meaning': 'open_app',
            'entities': {'app_name': 'WhatsApp'}
        }
        
        cmd = self.bridge._extract_command_from_nlp(nlp_result, "Abre o WhatsApp")
        
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.command_type, CommandType.OPEN_APP)
        self.assertEqual(cmd.action, 'open_app')
    
    def test_extract_command_send_message(self):
        """Testa extração de comando para enviar mensagem."""
        nlp_result = {
            'confidence': 0.85,
            'semantic_meaning': 'message',
            'entities': {'recipient': 'João', 'text': 'Oi'}
        }
        
        cmd = self.bridge._extract_command_from_nlp(nlp_result, "Manda mensagem para João")
        
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.command_type, CommandType.SEND_MESSAGE)


if __name__ == '__main__':
    unittest.main()
