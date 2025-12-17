import logging
import re
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CommandType(Enum):
    """Tipos de comandos suportados."""
    OPEN_APP = "open_app"
    CLOSE_APP = "close_app"
    SEND_MESSAGE = "send_message"
    OPEN_URL = "open_url"
    CALL = "call"
    TAKE_SCREENSHOT = "take_screenshot"
    SET_BRIGHTNESS = "set_brightness"
    GENERIC = "generic"

@dataclass
class ParsedCommand:
    """Representa um comando parseado."""
    command_type: CommandType
    action: str
    parameters: Dict[str, Any]
    confidence: float
    raw_input: str

class CommandParser:
    """
    Parser avancado de comandos para o Agente Smith.
    Week 2: Suporta comandos naturais em portugues.
    """
    
    def __init__(self):
        """Inicializa o parser de comandos."""
        self.command_patterns = self._initialize_patterns()
        self.command_history: List[ParsedCommand] = []
    
    def _initialize_patterns(self) -> Dict[str, Dict[str, Any]]:
        """
        Inicializa padroes de comandos em portugues.
        
        Returns:
            Dicionario com padroes de comandos
        """
        return {
            'open_app': {
                'patterns': [
                    r'abr[ea]\s+(?:o|a)?\s+(.+)',
                    r'abre\s+(.+)',
                    r'open\s+(.+)',
                    r'inicia\s+(.+)',
                ],
                'type': CommandType.OPEN_APP,
                'confidence': 0.9
            },
            'close_app': {
                'patterns': [
                    r'fecha\s+(?:o|a)?\s+(.+)',
                    r'fech[ea]\s+(.+)',
                    r'close\s+(.+)',
                    r'encerra\s+(.+)',
                ],
                'type': CommandType.CLOSE_APP,
                'confidence': 0.9
            },
            'send_message': {
                'patterns': [
                    r'enviar?\s+(?:mensagem|msg|whatsapp)?\s+(?:para|a)?\s+(.+)\s+(?:dizendo|mensagem|msg)?\s+(.+)',
                    r'manda?\s+(?:mensagem|msg)?\s+(?:para|a)?\s+(.+)\s+(.+)',
                ],
                'type': CommandType.SEND_MESSAGE,
                'confidence': 0.85
            },
            'open_url': {
                'patterns': [
                    r'abr[ea]\s+(?:site|url|pagina)?\s+(.+)',
                    r'acessar?\s+(?:site|url)?\s+(.+)',
                ],
                'type': CommandType.OPEN_URL,
                'confidence': 0.85
            },
            'call': {
                'patterns': [
                    r'ligar?\s+(?:para)?\s+(.+)',
                    r'call\s+(.+)',
                    r'telefon[ae]r?\s+(?:para)?\s+(.+)',
                ],
                'type': CommandType.CALL,
                'confidence': 0.9
            },
            'screenshot': {
                'patterns': [
                    r'captura?(?:\s+de)?\s+tela',
                    r'screenshot',
                    r'print\s+screen',
                ],
                'type': CommandType.TAKE_SCREENSHOT,
                'confidence': 0.95
            },
        }
    
    def parse(self, input_text: str) -> Optional[ParsedCommand]:
        """
        Faz parse de um texto de entrada para um comando estruturado.
        
        Args:
            input_text: Texto com o comando
            
        Returns:
            ParsedCommand ou None se nao conseguir fazer parse
        """
        if not input_text or not input_text.strip():
            return None
        
        input_text = input_text.lower().strip()
        best_match = None
        best_confidence = 0
        
        # Tenta encontrar o melhor match
        for cmd_name, cmd_info in self.command_patterns.items():
            for pattern in cmd_info['patterns']:
                match = re.search(pattern, input_text)
                if match:
                    confidence = cmd_info['confidence']
                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_match = {
                            'type': cmd_info['type'],
                            'match': match,
                            'pattern': pattern,
                            'confidence': confidence
                        }
        
        if best_match:
            return self._create_parsed_command(
                input_text,
                best_match['type'],
                best_match['match'],
                best_match['confidence']
            )
        
        logger.warning(f"Nao foi possivel fazer parse do comando: {input_text}")
        return None
    
    def _create_parsed_command(self, input_text: str, cmd_type: CommandType,
                              match, confidence: float) -> ParsedCommand:
        """
        Cria um objeto ParsedCommand baseado no match.
        
        Args:
            input_text: Texto original
            cmd_type: Tipo do comando
            match: Match do regex
            confidence: Confianca do match
            
        Returns:
            ParsedCommand
        """
        parameters = {}
        
        # Extrai parametros baseado no tipo de comando
        groups = match.groups()
        if groups:
            if cmd_type == CommandType.OPEN_APP:
                parameters['app_name'] = groups[0].strip()
            elif cmd_type == CommandType.CLOSE_APP:
                parameters['app_name'] = groups[0].strip()
            elif cmd_type == CommandType.SEND_MESSAGE:
                parameters['recipient'] = groups[0].strip() if len(groups) > 0 else None
                parameters['message'] = groups[1].strip() if len(groups) > 1 else None
            elif cmd_type == CommandType.OPEN_URL:
                parameters['url'] = groups[0].strip()
            elif cmd_type == CommandType.CALL:
                parameters['phone_number'] = groups[0].strip()
        
        parsed_cmd = ParsedCommand(
            command_type=cmd_type,
            action=cmd_type.value,
            parameters=parameters,
            confidence=confidence,
            raw_input=input_text
        )
        
        self.command_history.append(parsed_cmd)
        logger.info(f"Comando parseado: {cmd_type.value} com confianca {confidence}")
        
        return parsed_cmd
    
    def get_command_history(self, limit: Optional[int] = None) -> List[ParsedCommand]:
        """
        Retorna historico de comandos parseados.
        
        Args:
            limit: Limitar resultados
            
        Returns:
            Lista de ParsedCommand
        """
        if limit:
            return self.command_history[-limit:]
        return self.command_history
    
    def clear_history(self) -> None:
        """
        Limpa o historico de comandos.
        """
        self.command_history.clear()
        logger.info("Historico de comandos limpo")
    
    def add_custom_pattern(self, command_type: CommandType, pattern: str,
                          confidence: float = 0.8) -> None:
        """
        Adiciona um padrao customizado de comando.
        
        Args:
            command_type: Tipo do comando
            pattern: Padrao regex
            confidence: Confianca do padrao
        """
        # Encontra ou cria entrada para este tipo
        found = False
        for cmd_name, cmd_info in self.command_patterns.items():
            if cmd_info['type'] == command_type:
                cmd_info['patterns'].append(pattern)
                found = True
                break
        
        if not found:
            self.command_patterns[command_type.value] = {
                'patterns': [pattern],
                'type': command_type,
                'confidence': confidence
            }
        
        logger.info(f"Padrao customizado adicionado para {command_type.value}")
