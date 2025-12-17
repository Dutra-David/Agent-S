#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ML Enhanced NLP - FastText + spaCy Integration
Week 4: Advanced Intent Classification and Entity Extraction
"""

import fasttext
import spacy
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class MLEnhancedResult:
    """Resultado do processamento ML combinado"""
    text: str
    intent: str
    confidence: float
    entities: Dict[str, List[str]]
    timestamp: datetime

class MLEnhancedNLP:
    """
    Combina FastText (intent classification) + spaCy (entity extraction)
    para processamento avancado de comandos em portugues.
    """
    
    def __init__(self):
        self.fasttext_model = None
        self.spacy_nlp = None
        self._initialize()
    
    def _initialize(self) -> None:
        """Inicializa modelos FastText e spaCy"""
        try:
            # Carrega FastText
            fasttext_path = Path("models/intent_classifier.bin")
            if fasttext_path.exists():
                self.fasttext_model = fasttext.load_model(str(fasttext_path))
                logger.info("FastText modelo carregado")
            else:
                logger.warning(f"FastText modelo nao encontrado: {fasttext_path}")
            
            # Carrega spaCy
            try:
                self.spacy_nlp = spacy.load("pt_core_news_md")
                logger.info("spaCy modelo carregado")
            except:
                logger.error("spaCy modelo pt_core_news_md nao encontrado")
                logger.info("Instale com: python -m spacy download pt_core_news_md")
        
        except Exception as e:
            logger.error(f"Erro ao inicializar modelos: {e}")
    
    def process(self, text: str) -> Optional[MLEnhancedResult]:
        """
        Processa texto com FastText + spaCy.
        
        Args:
            text: Texto para processar
        
        Returns:
            MLEnhancedResult ou None
        """
        if not text or not text.strip():
            return None
        
        try:
            # 1. Classifica intencao com FastText
            intent, confidence = self._classify_intent(text)
            
            # 2. Extrai entidades com spaCy
            entities = self._extract_entities(text)
            
            return MLEnhancedResult(
                text=text,
                intent=intent,
                confidence=confidence,
                entities=entities,
                timestamp=datetime.now()
            )
        
        except Exception as e:
            logger.error(f"Erro ao processar: {e}")
            return None
    
    def _classify_intent(self, text: str) -> Tuple[str, float]:
        """
        Classifica intencao usando FastText.
        
        Returns:
            Tupla (intent, confidence)
        """
        if not self.fasttext_model:
            return "unknown", 0.0
        
        try:
            labels, scores = self.fasttext_model.predict(text, k=1)
            intent = labels[0].replace("__label__", "")
            confidence = float(scores[0])
            return intent, confidence
        
        except:
            return "unknown", 0.0
    
    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extrai entidades usando spaCy.
        
        Returns:
            Dicionario com entidades por tipo
        """
        if not self.spacy_nlp:
            return {}
        
        try:
            doc = self.spacy_nlp(text)
            
            entities = {
                'persons': [],
                'times': [],
                'dates': [],
                'locations': [],
                'organizations': []
            }
            
            for ent in doc.ents:
                if ent.label_ == "PERSON":
                    entities['persons'].append(ent.text)
                elif ent.label_ == "TIME":
                    entities['times'].append(ent.text)
                elif ent.label_ == "DATE":
                    entities['dates'].append(ent.text)
                elif ent.label_ == "GPE":
                    entities['locations'].append(ent.text)
                elif ent.label_ == "ORG":
                    entities['organizations'].append(ent.text)
            
            return entities
        
        except Exception as e:
            logger.error(f"Erro ao extrair entidades: {e}")
            return {}

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    processor = MLEnhancedNLP()
    
    # Testes
    test_inputs = [
        "Abre o WhatsApp",
        "Manda mensagem para Joao",
        "Agenda reuniao amanha as 14h",
        "Liga para Maria na empresa",
        "Fecha o Telegram"
    ]
    
    print("\n=== Testes ML Enhanced NLP ===")
    for text in test_inputs:
        result = processor.process(text)
        if result:
            print(f"\nTexto: {result.text}")
            print(f"Intent: {result.intent} ({result.confidence:.1%})")
            print(f"Entities: {result.entities}")
