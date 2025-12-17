import os
import json
import logging
import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecurityLevel(Enum):
    """Niveis de seguranca para operacoes."""
    BAIXA = "baixa"
    MEDIA = "media"
    ALTA = "alta"
    CRITICA = "critica"

class SecurityManager:
    """
    Gerencia autenticacao, autorizacao e seguranca do Agente Smith.
    Week 1: Autenticacao basica e controle de acesso.
    """
    
    def __init__(self, admin_key: str, encryption_key: Optional[str] = None):
        """
        Inicializa gerenciador de seguranca.
        
        Args:
            admin_key: Chave mestre para autenticacao
            encryption_key: Chave para criptografia de dados sensiveis
        """
        self.admin_key = admin_key
        self.encryption_key = encryption_key or "default_key"
        self.logged_users: Dict[str, Dict] = {}
        self.blocked_users: List[str] = []
        self.operation_log: List[Dict] = []
        self.session_timeout = 3600  # 1 hora
        
    def authenticate(self, user_id: str, password: str) -> Tuple[bool, str]:
        """
        Autentica um usuario.
        
        Args:
            user_id: ID do usuario
            password: Senha do usuario
            
        Returns:
            Tuple[bool, str]: (sucesso, mensagem ou token)
        """
        try:
            if user_id in self.blocked_users:
                logger.warning(f"Tentativa de login com usuario bloqueado: {user_id}")
                return False, "Usuario bloqueado por seguranca"
            
            # Verifica credenciais (implementacao basica)
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            if password_hash == self.admin_key:
                token = self._generate_token(user_id)
                self.logged_users[user_id] = {
                    'token': token,
                    'login_time': datetime.now(),
                    'last_activity': datetime.now()
                }
                logger.info(f"Usuario autenticado: {user_id}")
                return True, token
            else:
                logger.warning(f"Falha de autenticacao para usuario: {user_id}")
                return False, "Credenciais invalidas"
        except Exception as e:
            logger.error(f"Erro durante autenticacao: {str(e)}")
            return False, f"Erro: {str(e)}"
    
    def authorize(self, user_id: str, action: str, resource: str) -> bool:
        """
        Verifica se usuario tem permissao para executar acao.
        
        Args:
            user_id: ID do usuario
            action: Acao a ser executada
            resource: Recurso a ser acessado
            
        Returns:
            bool: True se autorizado
        """
        try:
            # Implementacao basica - todos os usuarios autenticados tem acesso
            if user_id not in self.logged_users:
                return False
            
            # Verifica timeout de sessao
            session = self.logged_users[user_id]
            last_activity = session['last_activity']
            if datetime.now() - last_activity > timedelta(seconds=self.session_timeout):
                del self.logged_users[user_id]
                return False
            
            # Atualiza ultima atividade
            session['last_activity'] = datetime.now()
            
            logger.info(f"Autorizacao concedida: {user_id} - {action} - {resource}")
            self._log_operation(user_id, action, resource, "PERMITIDO")
            return True
        except Exception as e:
            logger.error(f"Erro durante autorizacao: {str(e)}")
            return False
    
    def validate_input(self, user_input: str, input_type: str = "comando") -> Tuple[bool, str]:
        """
        Valida entrada do usuario contra ataques.
        
        Args:
            user_input: Entrada a ser validada
            input_type: Tipo de entrada
            
        Returns:
            Tuple[bool, str]: (valido, mensagem)
        """
        try:
            # Validacoes basicas
            if len(user_input) > 1000:
                return False, "Entrada muito longa"
            
            # Detecta padroes suspeitos
            dangerous_patterns = [";", "'", '"', "exec", "eval", "__"]
            for pattern in dangerous_patterns:
                if pattern in user_input.lower():
                    logger.warning(f"Padrao suspeito detectado: {pattern}")
                    return False, "Entrada contem caracteres nao permitidos"
            
            return True, "Entrada valida"
        except Exception as e:
            logger.error(f"Erro durante validacao: {str(e)}")
            return False, f"Erro: {str(e)}"
    
    def _generate_token(self, user_id: str) -> str:
        """
        Gera token de sessao para o usuario.
        
        Args:
            user_id: ID do usuario
            
        Returns:
            str: Token gerado
        """
        timestamp = str(datetime.now().timestamp())
        message = f"{user_id}{timestamp}".encode()
        token = hmac.new(
            self.encryption_key.encode(),
            message,
            hashlib.sha256
        ).hexdigest()
        return token
    
    def _log_operation(self, user_id: str, action: str, resource: str, status: str):
        """
        Registra operacao para auditoria.
        
        Args:
            user_id: ID do usuario
            action: Acao executada
            resource: Recurso afetado
            status: Status da operacao
        """
        self.operation_log.append({
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'action': action,
            'resource': resource,
            'status': status
        })
    
    def logout(self, user_id: str) -> bool:
        """
        Faz logout de um usuario.
        
        Args:
            user_id: ID do usuario
            
        Returns:
            bool: True se logout bem-sucedido
        """
        try:
            if user_id in self.logged_users:
                del self.logged_users[user_id]
                logger.info(f"Usuario desconectado: {user_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Erro ao fazer logout: {str(e)}")
            return False
    
    def get_audit_log(self) -> List[Dict]:
        """
        Retorna log de auditoria.
        
        Returns:
            List[Dict]: Lista de operacoes registradas
        """
        return self.operation_log
