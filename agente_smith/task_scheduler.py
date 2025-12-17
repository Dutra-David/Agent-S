import logging
import threading
from typing import Dict, List, Callable, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TaskType(Enum):
    """Tipos de tarefas."""
    ONE_TIME = "one_time"
    RECURRING = "recurring"
    INTERVAL = "interval"

class TaskStatus(Enum):
    """Status de uma tarefa."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class Task:
    """Representa uma tarefa agendada."""
    id: str
    name: str
    task_type: TaskType
    callback: Callable
    scheduled_time: Optional[datetime] = None
    interval_seconds: Optional[int] = None
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    args: tuple = ()
    kwargs: dict = field(default_factory=dict)

class TaskScheduler:
    """
    Agendador de tarefas para Agente Smith.
    Week 2: Execucao de tarefas agendadas.
    """
    
    def __init__(self):
        """Inicializa o agendador de tarefas."""
        self.tasks: Dict[str, Task] = {}
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.completed_tasks: List[Task] = []
    
    def start(self) -> None:
        """Inicia o agendador."""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.thread.start()
        logger.info("Agendador de tarefas iniciado")
    
    def stop(self) -> None:
        """Para o agendador."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("Agendador de tarefas parado")
    
    def schedule_once(self, task_id: str, name: str, callback: Callable,
                     run_at: datetime, args: tuple = (), 
                     kwargs: dict = None) -> Task:
        """Agenda uma tarefa para rodar uma vez.
        
        Args:
            task_id: ID unico da tarefa
            name: Nome da tarefa
            callback: Funcao a executar
            run_at: Quando executar
            args: Argumentos posicionais
            kwargs: Argumentos nomeados
            
        Returns:
            Tarefa criada
        """
        task = Task(
            id=task_id,
            name=name,
            task_type=TaskType.ONE_TIME,
            callback=callback,
            scheduled_time=run_at,
            args=args,
            kwargs=kwargs or {}
        )
        self.tasks[task_id] = task
        logger.info(f"Tarefa '{name}' agendada para {run_at}")
        return task
    
    def schedule_interval(self, task_id: str, name: str, callback: Callable,
                         interval_seconds: int, args: tuple = (),
                         kwargs: dict = None) -> Task:
        """Agenda uma tarefa para rodar periodicamente.
        
        Args:
            task_id: ID unico da tarefa
            name: Nome da tarefa
            callback: Funcao a executar
            interval_seconds: Intervalo em segundos
            args: Argumentos posicionais
            kwargs: Argumentos nomeados
            
        Returns:
            Tarefa criada
        """
        task = Task(
            id=task_id,
            name=name,
            task_type=TaskType.INTERVAL,
            callback=callback,
            interval_seconds=interval_seconds,
            args=args,
            kwargs=kwargs or {}
        )
        self.tasks[task_id] = task
        logger.info(f"Tarefa '{name}' agendada para rodar a cada {interval_seconds}s")
        return task
    
    def cancel(self, task_id: str) -> bool:
        """Cancela uma tarefa.
        
        Args:
            task_id: ID da tarefa
            
        Returns:
            True se cancelada com sucesso
        """
        if task_id in self.tasks:
            self.tasks[task_id].status = TaskStatus.CANCELLED
            del self.tasks[task_id]
            logger.info(f"Tarefa {task_id} cancelada")
            return True
        return False
    
    def _scheduler_loop(self) -> None:
        """Loop principal do agendador."""
        last_run: Dict[str, datetime] = {}
        
        while self.running:
            now = datetime.now()
            
            for task_id, task in list(self.tasks.items()):
                try:
                    should_run = False
                    
                    if task.task_type == TaskType.ONE_TIME:
                        should_run = now >= task.scheduled_time
                    elif task.task_type == TaskType.INTERVAL:
                        last = last_run.get(task_id)
                        if last is None or (now - last).total_seconds() >= task.interval_seconds:
                            should_run = True
                            last_run[task_id] = now
                    
                    if should_run:
                        self._execute_task(task)
                        
                        if task.task_type == TaskType.ONE_TIME:
                            self.tasks.pop(task_id, None)
                            self.completed_tasks.append(task)
                
                except Exception as e:
                    logger.error(f"Erro ao executar tarefa {task_id}: {str(e)}")
                    task.status = TaskStatus.FAILED
            
            time.sleep(1)  # Verifica a cada segundo
    
    def _execute_task(self, task: Task) -> None:
        """Executa uma tarefa.
        
        Args:
            task: Tarefa a executar
        """
        try:
            task.status = TaskStatus.RUNNING
            task.callback(*task.args, **task.kwargs)
            task.status = TaskStatus.COMPLETED
            logger.info(f"Tarefa '{task.name}' executada com sucesso")
        except Exception as e:
            logger.error(f"Erro ao executar tarefa '{task.name}': {str(e)}")
            task.status = TaskStatus.FAILED
    
    def get_tasks(self) -> Dict[str, Task]:
        """Retorna todas as tarefas pendentes.
        
        Returns:
            Dicionario de tarefas
        """
        return self.tasks.copy()
    
    def get_completed_tasks(self, limit: Optional[int] = None) -> List[Task]:
        """Retorna tarefas completadas.
        
        Args:
            limit: Limitar resultados
            
        Returns:
            Lista de tarefas
        """
        if limit:
            return self.completed_tasks[-limit:]
        return self.completed_tasks
