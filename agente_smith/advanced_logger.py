#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced Logger System - Logging avançado com múltiplos níveis
Week 3: Sistema de logging com suporte a arquivo, console e métricas
"""

import logging
import logging.handlers
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import json
import sys
from enum import Enum


class LogLevel(Enum):
    """Níveis de logging disponíveis."""
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


class AdvancedLogger:
    """
    Sistema de logging avançado para Agente Smith.
    Suporta: console, arquivo, JSON, métricas.
    """
    
    def __init__(self, name: str, log_dir: str = "logs", 
                 log_level: LogLevel = LogLevel.INFO):
        """
        Inicializa o logger avançado.
        
        Args:
            name: Nome do logger
            log_dir: Diretório para logs
            log_level: Nível de logging inicial
        """
        self.name = name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True, parents=True)
        self.log_level = log_level
        
        # Criar logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(log_level.value)
        
        # Remover handlers antigos
        self.logger.handlers.clear()
        
        # Métricas
        self.metrics: Dict[str, int] = {
            'debug': 0,
            'info': 0,
            'warning': 0,
            'error': 0,
            'critical': 0
        }
        
        self._setup_handlers()
    
    def _setup_handlers(self) -> None:
        """
        Configura os handlers de logging.
        - Console (colorizado)
        - Arquivo rotativo (general)
        - Arquivo JSON (estruturado)
        - Arquivo de erros
        """
        # 1. Handler para Console
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.log_level.value)
        console_formatter = logging.Formatter(
            '%(asctime)s | %(name)s | %(levelname)-8s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # 2. Handler para arquivo principal (rotativo)
        general_log = self.log_dir / f"{self.name}.log"
        general_handler = logging.handlers.RotatingFileHandler(
            general_log,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        general_handler.setLevel(self.log_level.value)
        general_formatter = logging.Formatter(
            '%(asctime)s | %(name)s | %(levelname)s | %(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        general_handler.setFormatter(general_formatter)
        self.logger.addHandler(general_handler)
        
        # 3. Handler para erros
        error_log = self.log_dir / f"{self.name}_errors.log"
        error_handler = logging.handlers.RotatingFileHandler(
            error_log,
            maxBytes=10*1024*1024,
            backupCount=3,
            level=logging.WARNING
        )
        error_formatter = logging.Formatter(
            '%(asctime)s | %(name)s | %(levelname)s | %(funcName)s:%(lineno)d | %(exc_info)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        error_handler.setFormatter(error_formatter)
        self.logger.addHandler(error_handler)
        
        # 4. Handler para JSON (estruturado)
        json_log = self.log_dir / f"{self.name}_structured.json"
        self.json_log_path = json_log
    
    def _log_json(self, level: str, message: str, **kwargs) -> None:
        """
        Registra um log em formato JSON estruturado.
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'logger': self.name,
            'message': message,
            'extra': kwargs
        }
        
        try:
            with open(self.json_log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        except Exception as e:
            self.logger.error(f"Erro ao registrar JSON: {e}")
    
    def debug(self, message: str, **kwargs) -> None:
        """Log de debug."""
        self.logger.debug(message)
        self.metrics['debug'] += 1
        self._log_json('DEBUG', message, **kwargs)
    
    def info(self, message: str, **kwargs) -> None:
        """Log de informação."""
        self.logger.info(message)
        self.metrics['info'] += 1
        self._log_json('INFO', message, **kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        """Log de aviso."""
        self.logger.warning(message)
        self.metrics['warning'] += 1
        self._log_json('WARNING', message, **kwargs)
    
    def error(self, message: str, exception: Optional[Exception] = None, **kwargs) -> None:
        """Log de erro."""
        if exception:
            self.logger.error(message, exc_info=exception)
        else:
            self.logger.error(message)
        self.metrics['error'] += 1
        self._log_json('ERROR', message, exception=str(exception) if exception else None, **kwargs)
    
    def critical(self, message: str, exception: Optional[Exception] = None, **kwargs) -> None:
        """Log crítico."""
        if exception:
            self.logger.critical(message, exc_info=exception)
        else:
            self.logger.critical(message)
        self.metrics['critical'] += 1
        self._log_json('CRITICAL', message, exception=str(exception) if exception else None, **kwargs)
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Retorna métricas de logging.
        
        Returns:
            Dictãrio com métricas
        """
        total = sum(self.metrics.values())
        return {
            'total_logs': total,
            'breakdown': self.metrics.copy(),
            'debug_percentage': (self.metrics['debug'] / total * 100) if total > 0 else 0,
            'error_percentage': ((self.metrics['error'] + self.metrics['critical']) / total * 100) if total > 0 else 0
        }
    
    def reset_metrics(self) -> None:
        """
        Reseta as métricas de logging.
        """
        for key in self.metrics:
            self.metrics[key] = 0
        self.info("Métricas de logging resetadas")
    
    def set_level(self, level: LogLevel) -> None:
        """
        Altera o nível de logging.
        
        Args:
            level: Novo nível de logging
        """
        self.log_level = level
        self.logger.setLevel(level.value)
        for handler in self.logger.handlers:
            handler.setLevel(level.value)
        self.info(f"Nível de logging alterado para {level.name}")


# Global logger instance
_default_logger: Optional[AdvancedLogger] = None


def get_logger(name: str, log_dir: str = "logs", 
              log_level: LogLevel = LogLevel.INFO) -> AdvancedLogger:
    """
    Obtém uma instância do logger.
    
    Args:
        name: Nome do logger
        log_dir: Diretório para logs
        log_level: Nível de logging
        
    Returns:
        Instância do AdvancedLogger
    """
    return AdvancedLogger(name, log_dir, log_level)


def get_default_logger() -> AdvancedLogger:
    """
    Obtém o logger padrão global.
    """
    global _default_logger
    if _default_logger is None:
        _default_logger = AdvancedLogger("agente_smith", "logs", LogLevel.INFO)
    return _default_logger


if __name__ == "__main__":
    # Demonstração
    logger = get_logger("demo", log_level=LogLevel.DEBUG)
    
    logger.debug("Mensagem de debug", user_id=123)
    logger.info("Informação importante")
    logger.warning("Aviso de processamento", action="test")
    
    try:
        1 / 0
    except Exception as e:
        logger.error("Erro matemático", exception=e)
    
    # Métricas
    metrics = logger.get_metrics()
    print("\n=== Métricas de Logging ===")
    for key, value in metrics.items():
        print(f"{key}: {value}")
