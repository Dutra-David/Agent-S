import logging
from typing import Dict, List, Callable, Optional, Any
from datetime import datetime
from enum import Enum
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NotificationLevel(Enum):
    """Niveis de notificacao."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"

@dataclass
class Notification:
    """Representa uma notificacao."""
    title: str
    message: str
    level: NotificationLevel
    timestamp: datetime
    read: bool = False
    actions: Optional[Dict[str, Callable]] = None

class NotificationSystem:
    """
    Sistema de notificacoes para Agente Smith.
    Week 2: Notificacoes persistentes e callbacks.
    """
    
    def __init__(self):
        """Inicializa sistema de notificacoes."""
        self.notifications: List[Notification] = []
        self.subscribers: Dict[NotificationLevel, List[Callable]] = {
            level: [] for level in NotificationLevel
        }
        self.max_notifications = 100
    
    def send(self, title: str, message: str, 
             level: NotificationLevel = NotificationLevel.INFO,
             actions: Optional[Dict[str, Callable]] = None) -> Notification:
        """Envia uma notificacao.
        
        Args:
            title: Titulo da notificacao
            message: Mensagem
            level: Nivel de notificacao
            actions: Acoes customizadas
            
        Returns:
            Notificacao criada
        """
        notification = Notification(
            title=title,
            message=message,
            level=level,
            timestamp=datetime.now(),
            actions=actions
        )
        
        self.notifications.append(notification)
        if len(self.notifications) > self.max_notifications:
            self.notifications = self.notifications[-self.max_notifications:]
        
        # Notifica subscribers
        for callback in self.subscribers[level]:
            try:
                callback(notification)
            except Exception as e:
                logger.error(f"Erro ao executar callback: {str(e)}")
        
        logger.info(f"Notificacao enviada: {title}")
        return notification
    
    def subscribe(self, level: NotificationLevel, callback: Callable) -> None:
        """Inscreve callback para notificacoes.
        
        Args:
            level: Nivel de notificacao
            callback: Funcao callback
        """
        if callback not in self.subscribers[level]:
            self.subscribers[level].append(callback)
    
    def unsubscribe(self, level: NotificationLevel, callback: Callable) -> None:
        """Desinscreve callback.
        
        Args:
            level: Nivel de notificacao
            callback: Funcao callback
        """
        if callback in self.subscribers[level]:
            self.subscribers[level].remove(callback)
    
    def mark_as_read(self, notification: Notification) -> None:
        """Marca notificacao como lida.
        
        Args:
            notification: Notificacao a marcar
        """
        notification.read = True
    
    def get_unread(self) -> List[Notification]:
        """Retorna notificacoes nao lidas.
        
        Returns:
            Lista de notificacoes
        """
        return [n for n in self.notifications if not n.read]
    
    def clear(self) -> None:
        """Limpa todas as notificacoes."""
        self.notifications.clear()
        logger.info("Notificacoes limpas")
    
    def get_history(self, level: Optional[NotificationLevel] = None,
                   limit: Optional[int] = None) -> List[Notification]:
        """Retorna historico de notificacoes.
        
        Args:
            level: Filtrar por nivel
            limit: Limitar resultados
            
        Returns:
            Lista de notificacoes
        """
        history = self.notifications
        if level:
            history = [n for n in history if n.level == level]
        if limit:
            history = history[-limit:]
        return history
