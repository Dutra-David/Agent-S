import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Gerenciador de banco de dados local para Agente Smith.
    Week 2: Persistencia de dados com JSON.
    """
    
    def __init__(self, db_file: str = "agent_smith_db.json"):
        """Inicializa gerenciador de banco de dados.
        
        Args:
            db_file: Caminho do arquivo de banco de dados
        """
        self.db_file = db_file
        self.data = self._load_or_create_db()
    
    def _load_or_create_db(self) -> Dict[str, Any]:
        """Carrega ou cria banco de dados.
        
        Returns:
            Dicionario com dados do banco
        """
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                logger.info(f"Banco de dados carregado de {self.db_file}")
                return data
            except Exception as e:
                logger.error(f"Erro ao carregar banco de dados: {str(e)}")
        
        # Cria novo banco de dados
        data = {
            'users': {},
            'commands': [],
            'schedules': [],
            'settings': {},
            'contacts': {},
            'metadata': {'created_at': datetime.now().isoformat()}
        }
        self._save_db(data)
        return data
    
    def _save_db(self, data: Optional[Dict] = None) -> bool:
        """Salva banco de dados.
        
        Args:
            data: Dados a salvar (usa self.data se None)
            
        Returns:
            bool: True se salvo com sucesso
        """
        try:
            data = data or self.data
            with open(self.db_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar banco de dados: {str(e)}")
            return False
    
    def add_command(self, command: Dict[str, Any]) -> bool:
        """Adiciona comando ao historico.
        
        Args:
            command: Dados do comando
            
        Returns:
            bool: True se adicionado com sucesso
        """
        try:
            command['timestamp'] = datetime.now().isoformat()
            self.data['commands'].append(command)
            return self._save_db()
        except Exception as e:
            logger.error(f"Erro ao adicionar comando: {str(e)}")
            return False
    
    def get_commands(self, limit: Optional[int] = None) -> List[Dict]:
        """Retorna historico de comandos.
        
        Args:
            limit: Limitar resultados
            
        Returns:
            Lista de comandos
        """
        commands = self.data.get('commands', [])
        if limit:
            return commands[-limit:]
        return commands
    
    def add_contact(self, name: str, phone: str, metadata: Optional[Dict] = None) -> bool:
        """Adiciona contato ao banco de dados.
        
        Args:
            name: Nome do contato
            phone: Telefone do contato
            metadata: Dados adicionais
            
        Returns:
            bool: True se adicionado com sucesso
        """
        try:
            self.data['contacts'][name] = {
                'phone': phone,
                'added_at': datetime.now().isoformat(),
                'metadata': metadata or {}
            }
            return self._save_db()
        except Exception as e:
            logger.error(f"Erro ao adicionar contato: {str(e)}")
            return False
    
    def get_contact(self, name: str) -> Optional[Dict]:
        """Retorna dados de um contato.
        
        Args:
            name: Nome do contato
            
        Returns:
            Dados do contato ou None
        """
        return self.data['contacts'].get(name)
    
    def add_schedule(self, schedule: Dict[str, Any]) -> bool:
        """Adiciona agendamento.
        
        Args:
            schedule: Dados do agendamento
            
        Returns:
            bool: True se adicionado com sucesso
        """
        try:
            schedule['id'] = len(self.data['schedules']) + 1
            schedule['created_at'] = datetime.now().isoformat()
            self.data['schedules'].append(schedule)
            return self._save_db()
        except Exception as e:
            logger.error(f"Erro ao adicionar agendamento: {str(e)}")
            return False
    
    def get_schedules(self, active_only: bool = False) -> List[Dict]:
        """Retorna agendamentos.
        
        Args:
            active_only: Retornar apenas agendamentos ativos
            
        Returns:
            Lista de agendamentos
        """
        schedules = self.data.get('schedules', [])
        if active_only:
            schedules = [s for s in schedules if s.get('active', True)]
        return schedules
    
    def update_setting(self, key: str, value: Any) -> bool:
        """Atualiza configuracao.
        
        Args:
            key: Chave da configuracao
            value: Valor da configuracao
            
        Returns:
            bool: True se atualizado com sucesso
        """
        try:
            self.data['settings'][key] = value
            return self._save_db()
        except Exception as e:
            logger.error(f"Erro ao atualizar configuracao: {str(e)}")
            return False
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Retorna valor de configuracao.
        
        Args:
            key: Chave da configuracao
            default: Valor padrao se nao existir
            
        Returns:
            Valor da configuracao
        """
        return self.data['settings'].get(key, default)
    
    def clear_old_commands(self, days: int = 30) -> int:
        """Limpa comandos antigos.
        
        Args:
            days: Numero de dias
            
        Returns:
            Numero de comandos removidos
        """
        from datetime import timedelta
        cutoff = datetime.now() - timedelta(days=days)
        original_count = len(self.data['commands'])
        
        self.data['commands'] = [
            cmd for cmd in self.data['commands']
            if datetime.fromisoformat(cmd.get('timestamp', '')) > cutoff
        ]
        
        removed = original_count - len(self.data['commands'])
        if removed > 0:
            self._save_db()
        return removed
    
    def export_data(self, filepath: str) -> bool:
        """Exporta dados para arquivo.
        
        Args:
            filepath: Caminho do arquivo para exportar
            
        Returns:
            bool: True se exportado com sucesso
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            logger.info(f"Dados exportados para {filepath}")
            return True
        except Exception as e:
            logger.error(f"Erro ao exportar dados: {str(e)}")
            return False
