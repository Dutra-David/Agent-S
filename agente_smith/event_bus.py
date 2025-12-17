#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Event Bus - Sistema de eventos e observers
Week 3: Padrão observer para comunicação entre componentes
"""

from typing import Callable, Dict, List, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

from advanced_logger import get_logger, LogLevel

logger = get_logger("event_bus", log_level=LogLevel.INFO)


class EventType(Enum):
    """Tipos de eventos no sistema."""
    AGENT_STARTED = "agent_started"
    AGENT_STOPPED = "agent_stopped"
    COMMAND_RECEIVED = "command_received"
    COMMAND_EXECUTED = "command_executed"
    ERROR_OCCURRED = "error_occurred"
    CONFIG_CHANGED = "config_changed"
    VOICE_INPUT_DETECTED = "voice_input_detected"


@dataclass
class Event:
    """Representa um evento do sistema."""
    event_type: EventType
    data: Dict[str, Any]
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class EventBus:
    """
    Bus de eventos para comunicação entre componentes.
    Implementa o padrão observer.
    """
    
    def __init__(self):
        """
        Inicializa o event bus.
        """
        self._subscribers: Dict[EventType, List[Callable]] = {}
        self._event_history: List[Event] = []
        
        logger.info("EventBus inicializado")
    
    def subscribe(self, event_type: EventType, callback: Callable) -> None:
        """
        Subscreve a um tipo de evento.
        
        Args:
            event_type: Tipo do evento
            callback: Função a chamar quando evento é publicado
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        
        self._subscribers[event_type].append(callback)
        logger.debug(f"Subscriber adicionado para {event_type.value}")
    
    def unsubscribe(self, event_type: EventType, callback: Callable) -> None:
        """
        Remove subscriber de um tipo de evento.
        
        Args:
            event_type: Tipo do evento
            callback: Função a remover
        """
        if event_type in self._subscribers:
            try:
                self._subscribers[event_type].remove(callback)
                logger.debug(f"Subscriber removido para {event_type.value}")
            except ValueError:
                logger.warning(f"Subscriber não encontrado para {event_type.value}")
    
    def publish(self, event: Event) -> None:
        """
        Publica um evento para todos os subscribers.
        
        Args:
            event: Evento a publicar
        """
        self._event_history.append(event)
        
        if event.event_type in self._subscribers:
            for callback in self._subscribers[event.event_type]:
                try:
                    callback(event)
                except Exception as e:
                    logger.error(f"Erro ao executar callback: {e}", exception=e)
        
        logger.debug(f"Evento publicado: {event.event_type.value}")
    
    def emit(self, event_type: EventType, data: Dict[str, Any]) -> None:
        """
        Cria e publica um evento rapidamente.
        
        Args:
            event_type: Tipo do evento
            data: Dados do evento
        """
        event = Event(event_type=event_type, data=data)
        self.publish(event)
    
    def get_event_history(self, event_type: EventType = None, limit: int = 100) -> List[Event]:
        """
        Retorna histórico de eventos.
        
        Args:
            event_type: Filtrar por tipo (opcional)
            limit: Limitar número de eventos
            
        Returns:
            Lista de eventos
        """
        if event_type:
            events = [e for e in self._event_history if e.event_type == event_type]
        else:
            events = self._event_history
        
        return events[-limit:]
    
    def clear_history(self) -> None:
        """
        Limpa o histórico de eventos.
        """
        self._event_history.clear()
        logger.info("Histórico de eventos limpo")
    
    def get_subscriber_count(self, event_type: EventType = None) -> int:
        """
        Retorna número de subscribers.
        
        Args:
            event_type: Tipo do evento (opcional)
            
        Returns:
            Número de subscribers
        """
        if event_type:
            return len(self._subscribers.get(event_type, []))
        return sum(len(subs) for subs in self._subscribers.values())


# Instância global do event bus
_global_event_bus: EventBus = None


def get_event_bus() -> EventBus:
    """
    Obtém a instância global do event bus.
    """
    global _global_event_bus
    if _global_event_bus is None:
        _global_event_bus = EventBus()
    return _global_event_bus


if __name__ == "__main__":
    # Demo
    bus = get_event_bus()
    
    def on_command_received(event: Event):
        logger.info(f"Comando recebido: {event.data}")
    
    # Subscribe
    bus.subscribe(EventType.COMMAND_RECEIVED, on_command_received)
    
    # Publish events
    bus.emit(EventType.AGENT_STARTED, {"agent_name": "Agente Smith"})
    bus.emit(EventType.COMMAND_RECEIVED, {"command": "abrir whatsapp"})
    bus.emit(EventType.COMMAND_EXECUTED, {"result": "success"})
    
    # History
    history = bus.get_event_history()
    logger.info(f"Total de eventos: {len(history)}")
