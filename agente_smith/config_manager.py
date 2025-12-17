#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration Manager - Gerencia configurações em YAML/JSON
Week 3: Carregamento e validação de configurações
"""

import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict

from advanced_logger import get_logger, LogLevel

logger = get_logger("config_manager", log_level=LogLevel.INFO)


@dataclass
class AgentConfig:
    """Configuração principal do Agente Smith."""
    agent_name: str = "Agente Smith"
    version: str = "1.0.0"
    language: str = "pt-BR"
    debug_mode: bool = False
    log_level: str = "INFO"
    
    # Voice config
    enable_voice: bool = True
    voice_language: str = "pt-BR"
    
    # NLP config
    nlp_min_confidence: float = 0.7
    parser_min_confidence: float = 0.8
    
    # Database config
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "agente_smith"
    
    # Security
    admin_key: str = "default_key"
    enable_encryption: bool = True


class ConfigManager:
    """
    Gerencia configurações da aplicação em YAML/JSON.
    """
    
    def __init__(self, config_dir: str = "config"):
        """
        Inicializa o gerenciador de configurações.
        
        Args:
            config_dir: Diretório de configurações
        """
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True, parents=True)
        self.config: Dict[str, Any] = {}
        self.agent_config = AgentConfig()
        
        logger.info(f"ConfigManager inicializado com diretório: {config_dir}")
    
    def load_config(self, filename: str) -> Dict[str, Any]:
        """
        Carrega configuração de arquivo (YAML ou JSON).
        
        Args:
            filename: Nome do arquivo
            
        Returns:
            Dicionário com configurações
        """
        filepath = self.config_dir / filename
        
        if not filepath.exists():
            logger.warning(f"Arquivo de configuração não encontrado: {filepath}")
            return {}
        
        try:
            if filename.endswith('.yaml') or filename.endswith('.yml'):
                with open(filepath, 'r', encoding='utf-8') as f:
                    self.config = yaml.safe_load(f) or {}
            elif filename.endswith('.json'):
                with open(filepath, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            else:
                logger.error(f"Formato de arquivo não suportado: {filename}")
                return {}
            
            logger.info(f"Configuração carregada de: {filepath}")
            return self.config
            
        except Exception as e:
            logger.error(f"Erro ao carregar configuração: {e}", exception=e)
            return {}
    
    def save_config(self, filename: str, config: Optional[Dict[str, Any]] = None) -> bool:
        """
        Salva configuração em arquivo (YAML ou JSON).
        
        Args:
            filename: Nome do arquivo
            config: Dicionário de configuração (usa self.config se None)
            
        Returns:
            True se salvo com sucesso
        """
        filepath = self.config_dir / filename
        config_data = config or self.config
        
        try:
            if filename.endswith('.yaml') or filename.endswith('.yml'):
                with open(filepath, 'w', encoding='utf-8') as f:
                    yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)
            elif filename.endswith('.json'):
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(config_data, f, indent=2, ensure_ascii=False)
            else:
                logger.error(f"Formato de arquivo não suportado: {filename}")
                return False
            
            logger.info(f"Configuração salva em: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao salvar configuração: {e}", exception=e)
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Obtém valor de configuração.
        
        Args:
            key: Chave (suporta notação com ponto: "database.host")
            default: Valor padrão
            
        Returns:
            Valor da configuração
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """
        Define valor de configuração.
        
        Args:
            key: Chave (suporta notação com ponto)
            value: Novo valor
        """
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        logger.debug(f"Configuração alterada: {key} = {value}")
    
    def load_agent_config(self, filename: str = "agent_config.yaml") -> AgentConfig:
        """
        Carrega configuração do agente.
        
        Args:
            filename: Nome do arquivo
            
        Returns:
            Objeto AgentConfig
        """
        config_dict = self.load_config(filename)
        if config_dict:
            self.agent_config = AgentConfig(**config_dict)
        return self.agent_config
    
    def save_agent_config(self, filename: str = "agent_config.yaml") -> bool:
        """
        Salva configuração do agente.
        
        Args:
            filename: Nome do arquivo
            
        Returns:
            True se salvo com sucesso
        """
        return self.save_config(filename, asdict(self.agent_config))
    
    def validate_config(self) -> bool:
        """
        Valida configuração.
        
        Returns:
            True se válida
        """
        required_keys = ['agent_name', 'version', 'language']
        
        for key in required_keys:
            if key not in self.config:
                logger.error(f"Chave obrigatória ausente: {key}")
                return False
        
        logger.info("Configuração validada com sucesso")
        return True
    
    def list_configs(self) -> list:
        """
        Lista todos os arquivos de configuração.
        
        Returns:
            Lista de nomes de arquivos
        """
        configs = list(self.config_dir.glob('*.yaml')) + list(self.config_dir.glob('*.json'))
        return [c.name for c in configs]


if __name__ == "__main__":
    # Demo
    manager = ConfigManager("config")
    
    # Cria configuração padrão
    default_config = {
        'agent_name': 'Agente Smith',
        'version': '1.0.0',
        'language': 'pt-BR',
        'debug_mode': False,
        'log_level': 'INFO'
    }
    
    # Salva
    manager.save_config('agent_config.yaml', default_config)
    
    # Carrega
    loaded = manager.load_config('agent_config.yaml')
    logger.info(f"Configuração carregada: {loaded}")
