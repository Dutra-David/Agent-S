# ⚡ QUICK START - PowerShell (COPY & PASTE)

**Tempo**: 1h 40 min  
**Status**: 🟢 PRONTO PARA RODAR AGORA

---

## 🖥️ PASSO 0: ABRA PowerShell COMO ADMINISTRATOR

```
Win + X → PowerShell (Administrador)
OU
Pesquise "PowerShell" → Clique direito → Executar como Administrador
```

✅ Você deve ver: `PS C:\Users\...`

---

## 📋 COPIE E COLE CADA LINHA EM SEQUÊNCIA

### PASSO 1: Ir para a pasta (5 segundos)
```powershell
cd C:\Users\$env:USERNAME\Agent-S\agente_smith
```
✅ Resultado: `PS C:\Users\...\Agent-S\agente_smith>`

---

### PASSO 2: Verificar Python (10 segundos)
```powershell
python --version
```
✅ Esperado: `Python 3.10.x` ou superior

---

### PASSO 3: Sincronizar Git (30 segundos)
```powershell
git clean -fd
```

```powershell
git pull origin main
```

```powershell
git branch
```
✅ Esperado: `* main` (com asterisco)

---

### PASSO 4: Criar Virtual Env (10 segundos)
```powershell
python -m venv venv
```

---

### PASSO 5: Ativar Virtual Env (5 segundos)
```powershell
.\venv\Scripts\activate
```
✅ Agora você verá: `(venv) PS C:\...>`

---

### PASSO 6: Instalar Dependências (5 minutos)
```powershell
python -m pip install --upgrade pip
```

```powershell
pip install -r requirements.txt
```

```powershell
pip install fasttext
```

```powershell
pip install spacy
```

```powershell
python -m spacy download pt_core_news_md
```

✅ Aguarde terminar (pode demorar um pouco em fasttext)

---

### PASSO 7: Validar Instalação (30 segundos)
```powershell
python
```

Agora você está dentro do Python. Digite:
```python
>>> import fasttext
>>> import spacy
>>> nlp = spacy.load("pt_core_news_md")
>>> print("OK")
OK
>>> exit()
```

✅ Se viu "OK" e retornou ao PowerShell, tá certo!

---

## 🔧 PASSO 8: EDITAR nlp_command_bridge.py (45 minutos)

### Abrir arquivo no VS Code
```powershell
code nlp_command_bridge.py
```

### NO INÍCIO do arquivo, ADICIONE:
```python
from ml_enhanced_nlp import MLEnhancedNLP, MLEnhancedResult
import time
import logging

logger = logging.getLogger(__name__)
```

### ENCONTRE a classe NLPCommandBridge e NO __init__, ADICIONE:
```python
def __init__(self):
    self.ml_processor = MLEnhancedNLP()
    self.intent_handlers = {
        'open_app': self._handle_open_app,
        'close_app': self._handle_close_app,
        'send_message': self._handle_send_message,
        'call': self._handle_call,
        'take_screenshot': self._handle_screenshot,
        'schedule': self._handle_schedule,
        'open_url': self._handle_open_url,
        'help': self._handle_help,
    }
```

### ADICIONE o método process():
```python
def process(self, voice_input: str):
    """Processa entrada de voz com ML"""
    if not voice_input or not voice_input.strip():
        return None
    
    result = self.ml_processor.process(voice_input)
    if not result:
        return None
    
    handler = self.intent_handlers.get(result.intent)
    if handler:
        return handler(result)
    return None
```

### ADICIONE os 8 handlers:
```python
def _handle_open_app(self, result: MLEnhancedResult):
    logger.info(f"🚀 Abrindo app: {result.text}")
    return {"action": "open_app", "confidence": result.confidence, "text": result.text}

def _handle_close_app(self, result: MLEnhancedResult):
    logger.info("❌ Fechando app")
    return {"action": "close_app", "confidence": result.confidence}

def _handle_send_message(self, result: MLEnhancedResult):
    logger.info("💬 Enviando mensagem")
    return {"action": "send_message", "entities": result.entities}

def _handle_call(self, result: MLEnhancedResult):
    logger.info("☎️ Ligando")
    return {"action": "call", "entities": result.entities}

def _handle_screenshot(self, result: MLEnhancedResult):
    logger.info("📸 Capturando tela")
    return {"action": "screenshot"}

def _handle_schedule(self, result: MLEnhancedResult):
    logger.info("📅 Agendando tarefa")
    return {"action": "schedule", "entities": result.entities}

def _handle_open_url(self, result: MLEnhancedResult):
    logger.info("🌐 Abrindo URL")
    return {"action": "open_url", "entities": result.entities}

def _handle_help(self, result: MLEnhancedResult):
    logger.info("❓ Solicitando ajuda")
    return {"action": "help"}
```

✅ SALVE com Ctrl+S

---

## 📝 PASSO 9: Criar test_phase3_integration.py (5 minutos)

### Abrir novo arquivo
```powershell
code test_phase3_integration.py
```

### COPIE TODO este código:
```python
import unittest
from nlp_command_bridge import NLPCommandBridge
from ml_enhanced_nlp import MLEnhancedNLP

class Phase3Tests(unittest.TestCase):
    def setUp(self):
        self.bridge = NLPCommandBridge()
        self.processor = MLEnhancedNLP()
    
    def test_bridge_init(self):
        """Testa inicialização do bridge"""
        self.assertIsNotNone(self.bridge)
        self.assertIsNotNone(self.bridge.ml_processor)
        self.assertIsNotNone(self.bridge.intent_handlers)
    
    def test_open_app(self):
        """Testa comando 'abrir app'"""
        result = self.bridge.process("Abre o WhatsApp")
        self.assertIsNotNone(result)
        self.assertEqual(result['action'], 'open_app')
    
    def test_send_message(self):
        """Testa comando 'enviar mensagem'"""
        result = self.bridge.process("Manda mensagem para João")
        self.assertIsNotNone(result)
        self.assertEqual(result['action'], 'send_message')
    
    def test_take_screenshot(self):
        """Testa comando 'capturar tela'"""
        result = self.bridge.process("Tira uma screenshot")
        self.assertIsNotNone(result)
        self.assertEqual(result['action'], 'take_screenshot')

if __name__ == '__main__':
    unittest.main()
```

✅ SALVE com Ctrl+S

---

## 🧪 PASSO 10: RODAR OS TESTES (5 minutos)

### Volte ao PowerShell e rode:
```powershell
python -m pytest test_phase3_integration.py -v
```

### ✅ ESPERADO:
```
test_bridge_init PASSED
test_open_app PASSED
test_send_message PASSED
test_take_screenshot PASSED

======================== 4 passed in 0.50s ========================
```

---

## 📤 PASSO 11: Fazer Commit (3 minutos)

```powershell
git add .
```

```powershell
git status
```

```powershell
git commit -m "Phase 3: Complete ML integration, handlers, and tests on Windows"
```

```powershell
git push origin main
```

✅ Verifique no GitHub se os arquivos estão lá!

---

## ✨ FIM!

Se tudo deu certo, você completou a **FASE 3**! 🎉

**Checklist Final**:
- [ ] 4/4 testes passando
- [ ] Commits visíveis no GitHub
- [ ] nlp_command_bridge.py com 8 handlers
- [ ] test_phase3_integration.py criado

---

## 🆘 ERRO? Tente isso:

### "ModuleNotFoundError: No module named 'fasttext'"
```powershell
pip install --upgrade fasttext
```

### "(venv) não aparece no prompt"
```powershell
.\venv\Scripts\activate
```

### "Comando não reconhecido"
Certifique-se que está NO DIRETÓRIO CERTO:
```powershell
cd C:\Users\SEU_USUARIO\Agent-S\agente_smith
pwd  # Deve mostrar esse caminho
```

---

**PRONTO! Agora é só copiar, colar e rodar! 🚀**
