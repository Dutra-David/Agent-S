# Phase 2: Model Training Execution Plan

**Status:** 🟡 INICIANDO - Critical Phase
**Data:** 17 de Dezembro de 2025 - 17:00 BRT
**Estimado:** 2 dias

---

## Objetivo da Phase 2

Treinar o modelo FastText com os dados de intenção em português para alcançar:
- **Acurácia:** 94-96%
- **Performance:** <10ms por predição
- **Tamanho:** 2-5MB do modelo
- **Confiabilidade:** 100% de execução sem erros

---

## Checklist de Execução

### 1. Pré-requisitos & Setup

- [x] Repositório clonado em máquina local Windows
- [x] train_intents.txt validado (137 exemplos)
- [x] fasttext_trainer.py verificado (168 linhas)
- [ ] Python 3.10+ instalado
- [ ] pip atualizado
- [ ] Ambiente virtual criado

### 2. Instalação de Dependências

```bash
# 2a. Criar ambiente virtual
python -m venv venv
source venv/Scripts/activate  # Windows

# 2b. Instalar FastText
pip install fasttext

# 2c. Instalar spaCy (para Phase 3)
pip install spacy

# 2d. Baixar modelo português spaCy
python -m spacy download pt_core_news_md

# 2e. Instalar logging
pip install colorlog
```

**Checklist:**
- [ ] Ambiente virtual ativo
- [ ] fasttext==0.9.2+ instalado
- [ ] spacy==3.0+ instalado
- [ ] pt_core_news_md baixado

### 3. Validação de Dados de Treino

**Arquivo:** train_intents.txt

**Verificação:**
- [ ] 137 linhas de dados
- [ ] Formato correto: `__label__intent texto`
- [ ] 8 categorias de intenção:
  - [ ] open_app (15+ exemplos)
  - [ ] close_app (15+ exemplos)
  - [ ] send_message (20+ exemplos)
  - [ ] call (15+ exemplos)
  - [ ] take_screenshot (10+ exemplos)
  - [ ] schedule (15+ exemplos)
  - [ ] open_url (15+ exemplos)
  - [ ] help (10+ exemplos)

**Comando para validar:**
```bash
wc -l train_intents.txt
head -20 train_intents.txt
```

### 4. Execução do Treinamento

**Comando Principal:**
```bash
cd agente_smith
python fasttext_trainer.py
```

**Saída Esperada:**
```
=== FastText Trainer Inicializado ===
Iniciando treinamento FastText...
- Dataset: train_intents.txt
- Épocas: 25
- Taxa de aprendizado: 1.0

Modelo treinado com sucesso!
Salvo em: models/intent_classifier.bin

=== Métricas do Modelo ===
Exemplos testados: 137
Precisão: 0.9634
Recall: 0.9563
F1 Score: 0.9598

=== Testes de Predição ===
Abre o WhatsApp            → open_app       (95.2%)
Fecha o Telegram           → close_app      (92.1%)
Manda mensagem para João   → send_message   (98.3%)
Liga para Maria            → call           (91.5%)
Captura de tela            → take_screenshot (87.9%)
```

**Tempo Esperado de Execução:** 30-60 segundos

**Checklist:**
- [ ] Treinamento iniciado sem erros
- [ ] Progress bar visibilizado
- [ ] Métricas exibidas corretamente
- [ ] Modelo salvo em models/intent_classifier.bin

### 5. Validação do Modelo Treinado

**Arquivo Gerado:** models/intent_classifier.bin

**Verificação:**
```bash
# Verificar se arquivo existe
ls -lh models/intent_classifier.bin

# Saída esperada: ~2-5MB
```

**Checklist:**
- [ ] Arquivo exists: models/intent_classifier.bin
- [ ] Tamanho: 2-5MB
- [ ] ÃÚúêê de modificação: recente (dentro de 1 minuto)

### 6. Testes de Predição

**Métricas de Performance:**

| Métrica | Target | Esperado | Status |
|---------|--------|----------|--------|
| Precision | >94% | 96%+ | ⏳ |
| Recall | >94% | 95%+ | ⏳ |
| F1 Score | >94% | 95%+ | ⏳ |
| Tempo/pred | <10ms | 5-8ms | ⏳ |

**5 Testes Obrigatórios:**

1. **Teste: Open App**
   - Input: "Abre o WhatsApp"
   - Output esperado: open_app (>90%)
   - Status: [ ]

2. **Teste: Send Message**
   - Input: "Manda mensagem para João amanhã"
   - Output esperado: send_message (>90%)
   - Status: [ ]

3. **Teste: Schedule**
   - Input: "Agenda reunião às 14h"
   - Output esperado: schedule (>85%)
   - Status: [ ]

4. **Teste: Call**
   - Input: "Liga para Maria"
   - Output esperado: call (>88%)
   - Status: [ ]

5. **Teste: Help**
   - Input: "Me ajuda com isso"
   - Output esperado: help (>80%)
   - Status: [ ]

### 7. Documentação de Resultados

**Arquivo:** PHASE2_RESULTS.md (a criar)

**Conteudo a documentar:**
```
# Phase 2 - Results Report

## Data e Hora de Execução
- Data: [data]
- Hora: [hora]
- Duração: [tempo em segundos]

## Métricas Finais
- Precisão: [valor]
- Recall: [valor]
- F1 Score: [valor]

## Testes Executados
[Resultados de cada teste]

## Observações
[Qualquer observação relevante]
```

**Checklist:**
- [ ] Documento criado com timestamp
- [ ] Todas as métricas registradas
- [ ] Testes documentados
- [ ] Arquivo commitado no GitHub

### 8. Troubleshooting (Se necessário)

**Erro: "train_intents.txt not found"**
- Solução: Verifique se está no diretório correto (agente_smith)

**Erro: "No module named 'fasttext'"**
- Solução: pip install fasttext

**Erro: "Precisão < 90%"**
- Solução: Aumentar exemplos no train_intents.txt ou ajustar hyperparameters

**Aviso: "Modelo muito grande (>10MB)"**
- Solução: Normal para FastText, não é problema

---

## Timeline Estimado

**Total Estimado:** 2 dias (48 horas)

### Dia 1 (Today - 17/12)
- Setup e instalação de dependências: 30-45 min
- Validação de dados: 15 min
- Execução do treinamento: 1-2 min
- Validação inicial: 15 min

### Dia 2 (18/12)
- Testes extensivos de predição: 1-2 horas
- Ajustes e otimizações (se necessário): 1-2 horas
- Documentação final: 30 min
- Commit e preparação para Phase 3: 15 min

---

## Recursos Necessários

**Hardware:**
- RAM: 4GB mínimo (8GB recomendado)
- Processador: CPU modern (qualquer Intel/AMD i5+)
- Espaço em disco: 500MB

**Software:**
- Python 3.10+
- Git (para commits)
- Terminal/CMD
- Editor de texto (VS Code, etc)

**Documentação:**
- Este plano (PHASE2_MODEL_TRAINING_EXECUTION.md)
- WEEK4_IMPLEMENTATION.md
- WEEK4_COMPLETE_ANALYSIS.md

---

## Success Criteria

✅ **Phase 2 será considerada completa quando:**

1. ✅ Modelo treinado com sucesso sem erros
2. ✅ Accuracy >= 94%
3. ✅ Todos os 5 testes obrigatórios passarem
4. ✅ Tempo de predição < 10ms
5. ✅ Arquivo models/intent_classifier.bin gerado corretamente
6. ✅ Resultados documentados em PHASE2_RESULTS.md
7. ✅ Commit realizado no GitHub com métricas

---

## Próximas Fases

### Phase 3: Integração (Depois de Phase 2 ✅)

Após completar Phase 2:
- [ ] Integrar MLEnhancedNLP em nlp_command_bridge.py
- [ ] Atualizar requirements.txt
- [ ] Testes de integração
- [ ] Deploy em Windows

---

## Notas Importantes

📄 **Importante:**
- Não modificar train_intents.txt durante o treinamento
- Manter terminal aberto até conclusão do script
- Documentar QUALQUER erro ou aviso que ocorrer
- Se modelo ficar > 10MB, não é erro (FastText é assim mesmo)

---

## Contact & Support

**Projeto:** Agente Smith - Week 4 ML Enhancement
**Responsável:** Dutra-David
**GitHub:** https://github.com/Dutra-David/Agent-S
**Status:** Phase 2 - Model Training (CRITICAL)

---

*Última atualização: 17 de Dezembro de 2025 - 17:00 BRT*
*Status: 🟡 Ready for Execution*
