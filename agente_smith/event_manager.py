import logging
from datetime import datetime
from typing import Dict, List, Callable, Any, Optional
from enum import Enum
from collections import defaultdict

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EventType(Enum):
    """Tipos de eventos do Agente Smith."""
    # Eventos de dispositivo
    DEVICE_CONNECTED = "device_connected"
    DEVICE_DISCONNECTED = "device_disconnected"
    APP_OPENED = "app_opened"
    APP_CLOSED = "app_closed"
    
    # Eventos de voz
    VOICE_COMMAND_RECEIVED = "voice_command_received"
    VOICE_COMMAND_PROCESSED = "voice_command_processed"
    
    # Eventos de mensagem
    WHATSAPP_MESSAGE_RECEIVED = "whatsapp_message_received"
    WHATSAPP_MESSAGE_SENT = "whatsapp_message_sent"
    
    # Eventos de sistema
    AGENT_STARTED = "agent_started"
    AGENT_STOPPED = "agent_stopped"
    ERROR_OCCURRED = "error_occurred"

class Event:
    """Classe que representa um evento."""
    
    def __init__(self, event_type: EventType, data: Dict[str, Any], 
                 timestamp: Optional[datetime] = None):
        """
        Inicializa um evento.
        
        Args:
            event_type: Tipo do evento
            data: Dados associados ao evento
            timestamp: Timestamp do evento
        """
        self.event_type = event_type
        self.data = data
        self.timestamp = timestamp or datetime.now()
    
    def __repr__(self) -> str:
        return f"Event({self.event_type.value}, {self.timestamp})"

class EventManager:
    """
    Gerencia eventos e listeners para o Agente Smith.
    Week 2: Sistema de eventos com subscribers.
    """
    
    def __init__(self):
        """Inicializa o gerenciador de eventos."""
        self.listeners: Dict[EventType, List[Callable]] = defaultdict(list)
        self.event_history: List[Event] = []
        self.max_history = 1000  # Limite de historico
    
    def subscribe(self, event_type: EventType, callback: Callable) -> None:
        """
        Inscreve um callback para um tipo de evento.
        
        Args:
            event_type: Tipo de evento
            callback: Funcao callback a ser chamada
        """
        if callback not in self.listeners[event_type]:
            self.listeners[event_type].append(callback)
            logger.info(f"Listener inscrito para {event_type.value}")
    
    def unsubscribe(self, event_type: EventType, callback: Callable) -> None:
        """
        Desinscreve um callback de um tipo de evento.
        
        Args:
            event_type: Tipo de evento
            callback: Funcao callback a ser removida
        """
        if callback in self.listeners[event_type]:
            self.listeners[event_type].remove(callback)
            logger.info(f"Listener removido de {event_type.value}")
    
    def emit(self, event: Event) -> None:
        """
        Emite um evento para todos os listeners inscritos.
        
        Args:
            event: Evento a ser emitido
        """
        try:
            # Registra no historico
            self._add_to_history(event)
            
            # Chama todos os listeners
            listeners = self.listeners.get(event.event_type, [])
            logger.info(f"Emitindo evento {event.event_type.value} para {len(listeners)} listeners")
            
            for callback in listeners:
                try:
                    callback(event)
                except Exception as e:
                    logger.error(f"Erro ao chamar callback: {str(e)}")
                    # Emite evento de erro
                    error_event = Event(
                        EventType.ERROR_OCCURRED,
                        {'error': str(e), 'original_event': event.event_type.value}
                    )
                    self.emit(error_event)
        
        except Exception as e:
            logger.error(f"Erro ao emitir evento: {str(e)}")
    
    def emit_event(self, event_type: EventType, data: Dict[str, Any]) -> None:
        """
        Conveniencia para emitir um evento sem criar manualmente.
        
        Args:
            event_type: Tipo de evento
            data: Dados do evento
        """
        event = Event(event_type, data)
        self.emit(event)
    
    def _add_to_history(self, event: Event) -> None:
        """
        Adiciona evento ao historico.
        
        Args:
            event: Evento a ser adicionado
        """
        self.event_history.append(event)
        
        # Remove eventos antigos se exceder limite
        if len(self.event_history) > self.max_history:
            self.event_history = self.event_history[-self.max_history:]
    
    def get_history(self, event_type: Optional[EventType] = None,
                   limit: Optional[int] = None) -> List[Event]:
        """
        Retorna o historico de eventos.
        
        Args:
            event_type: Filtro por tipo de evento (opcional)
            limit: Limitar resultados
            
        Returns:
            Lista de eventos
        """
        history = self.event_history
        
        if event_type:
            history = [e for e in history if e.event_type == event_type]
        
        if limit:
            history = history[-limit:]
        
        return history
    
    def clear_history(self) -> None:
        """
        Limpa o historico de eventos.
        """
        self.event_history.clear()
        logger.info("Historico de eventos limpo")
    
    def get_listeners_count(self, event_type: EventType) -> int:
        """
        Retorna o numero de listeners para um tipo de evento.
        
        Args:
            event_type: Tipo de evento
            
        Returns:
            Numero de listeners
        """
        return len(self.listeners.get(event_type, []))
    
    def get_all_event_types_with_listeners(self) -> List[EventType]:
        """
        Retorna lista de tipos de eventos com listeners inscritos.
        
        Returns:
            Lista de EventTypes
        """
        return list(self.listeners.keys())
