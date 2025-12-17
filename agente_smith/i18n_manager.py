#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Internationalization Manager (i18n) - Suporte a múltiplos idiomas
Week 3: Tradução dinâmica de mensagens
"""

from typing import Dict, Optional, Any
from enum import Enum

from advanced_logger import get_logger, LogLevel

logger = get_logger("i18n_manager", log_level=LogLevel.INFO)


class Language(Enum):
    """Idiomas suportados."""
    PT_BR = "pt-BR"
    EN_US = "en-US"
    ES_ES = "es-ES"
    FR_FR = "fr-FR"


class I18nManager:
    """
    Gerenciador de internacionalização.
    Suporta múltiplos idiomas e tradução dinâmica.
    """
    
    def __init__(self, default_language: Language = Language.PT_BR):
        """
        Inicializa o i18n manager.
        
        Args:
            default_language: Idioma padrão
        """
        self.current_language = default_language
        self.translations: Dict[Language, Dict[str, str]] = {}
        self._load_default_translations()
        
        logger.info(f"I18nManager inicializado com idioma: {default_language.value}")
    
    def _load_default_translations(self) -> None:
        """
        Carrega as traduções padrão.
        """
        self.translations[Language.PT_BR] = {
            "welcome": "Bem-vindo ao Agente Smith",
            "farewell": "Até logo",
            "error": "Erro ao processar solicitação",
            "success": "Operação concluída com sucesso",
            "open_app": "Abrindo aplicativo",
            "close_app": "Fechando aplicativo",
            "send_message": "Enviando mensagem",
            "command_executed": "Comando executado"
        }
        
        self.translations[Language.EN_US] = {
            "welcome": "Welcome to Agente Smith",
            "farewell": "See you later",
            "error": "Error processing request",
            "success": "Operation completed successfully",
            "open_app": "Opening application",
            "close_app": "Closing application",
            "send_message": "Sending message",
            "command_executed": "Command executed"
        }
    
    def set_language(self, language: Language) -> None:
        """
        Define o idioma atual.
        
        Args:
            language: Novo idioma
        """
        self.current_language = language
        logger.info(f"Idioma alterado para: {language.value}")
    
    def translate(self, key: str, default: Optional[str] = None) -> str:
        """
        Traduz uma chave para o idioma atual.
        
        Args:
            key: Chave de tradução
            default: Valor padrão se não encontrado
            
        Returns:
            Texto traduzido
        """
        if self.current_language in self.translations:
            return self.translations[self.current_language].get(key, default or key)
        return default or key
    
    def add_translation(self, language: Language, key: str, translation: str) -> None:
        """
        Adiciona uma tradução.
        
        Args:
            language: Idioma
            key: Chave
            translation: Texto traduzido
        """
        if language not in self.translations:
            self.translations[language] = {}
        
        self.translations[language][key] = translation
        logger.debug(f"Tradução adicionada: {language.value}[{key}]")
    
    def get_available_languages(self) -> list:
        """
        Lista idiomas disponíveis.
        
        Returns:
            Lista de idiomas
        """
        return [lang.value for lang in self.translations.keys()]
    
    def get_current_language(self) -> str:
        """
        Retorna o idioma atual.
        
        Returns:
            Idioma atual
        """
        return self.current_language.value


# Instância global
_global_i18n: Optional[I18nManager] = None


def get_i18n() -> I18nManager:
    """
    Obtém a instância global do i18n manager.
    """
    global _global_i18n
    if _global_i18n is None:
        _global_i18n = I18nManager()
    return _global_i18n


def _(key: str, default: Optional[str] = None) -> str:
    """
    Função de conveniência para tradução.
    
    Args:
        key: Chave de tradução
        default: Valor padrão
        
    Returns:
        Texto traduzido
    """
    return get_i18n().translate(key, default)


if __name__ == "__main__":
    # Demo
    i18n = get_i18n()
    
    # Traduz em português
    print(_("welcome"))  # Bem-vindo ao Agente Smith
    print(_("success"))  # Operação concluída com sucesso
    
    # Muda para inglês
    i18n.set_language(Language.EN_US)
    print(_("welcome"))  # Welcome to Agente Smith
    print(_("success"))  # Operation completed successfully
    
    # Lista idiomas
    print(f"Idiomas disponíveis: {i18n.get_available_languages()}")
