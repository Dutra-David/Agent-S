import logging
import re
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SentimentType(Enum):
    """Tipos de sentimento."""
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"

@dataclass
class NLPResult:
    """Resultado de processamento NLP."""
    text: str
    tokens: List[str]
    entities: List[Dict[str, Any]]
    sentiment: SentimentType
    intent: str
    confidence: float

class NLPProcessor:
    """
    Processador de linguagem natural para Agente Smith.
    Week 3: NLP avancado com analise de sentimento e intencoes.
    """
    
    def __init__(self):
        """Inicializa processador NLP."""
        self.sentiment_words = self._load_sentiment_lexicon()
        self.intent_patterns = self._load_intent_patterns()
        self.stopwords = self._load_stopwords()
    
    def process(self, text: str) -> NLPResult:
        """Processa texto com NLP.
        
        Args:
            text: Texto a processar
            
        Returns:
            Resultado NLP
        """
        tokens = self.tokenize(text)
        entities = self.extract_entities(text)
        sentiment = self.analyze_sentiment(text)
        intent, confidence = self.detect_intent(text)
        
        return NLPResult(
            text=text,
            tokens=tokens,
            entities=entities,
            sentiment=sentiment,
            intent=intent,
            confidence=confidence
        )
    
    def tokenize(self, text: str) -> List[str]:
        """Tokeniza texto em palavras.
        
        Args:
            text: Texto a tokenizar
            
        Returns:
            Lista de tokens
        """
        text = text.lower()
        tokens = re.findall(r'\b\w+\b', text)
        return tokens
    
    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extrai entidades nomeadas.
        
        Args:
            text: Texto para extrair entidades
            
        Returns:
            Lista de entidades
        """
        entities = []
        
        # Detecta numeros
        numbers = re.findall(r'\d+', text)
        for num in numbers:
            entities.append({
                'type': 'NUMBER',
                'value': num,
                'text': num
            })
        
        # Detecta horas
        times = re.findall(r'\d{1,2}:\d{2}', text)
        for time in times:
            entities.append({
                'type': 'TIME',
                'value': time,
                'text': time
            })
        
        # Detecta emails
        emails = re.findall(r'[\w.-]+@[\w.-]+\.\w+', text)
        for email in emails:
            entities.append({
                'type': 'EMAIL',
                'value': email,
                'text': email
            })
        
        return entities
    
    def analyze_sentiment(self, text: str) -> SentimentType:
        """Analisa sentimento do texto.
        
        Args:
            text: Texto para analizar
            
        Returns:
            Tipo de sentimento
        """
        text_lower = text.lower()
        score = 0
        
        for word, sentiment in self.sentiment_words.items():
            if word in text_lower:
                score += sentiment
        
        if score > 0.5:
            return SentimentType.POSITIVE
        elif score < -0.5:
            return SentimentType.NEGATIVE
        else:
            return SentimentType.NEUTRAL
    
    def detect_intent(self, text: str) -> Tuple[str, float]:
        """Detecta intencao do usuario.
        
        Args:
            text: Texto para detectar intencao
            
        Returns:
            Tupla (intencao, confianca)
        """
        best_intent = "unknown"
        best_score = 0.0
        
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    score = 0.9
                    if score > best_score:
                        best_score = score
                        best_intent = intent
        
        return best_intent, best_score
    
    def _load_sentiment_lexicon(self) -> Dict[str, float]:
        """Carrega lexico de sentimento.
        
        Returns:
            Dicionario com palavras e scores
        """
        return {
            'otimo': 1.0,
            'adorei': 1.0,
            'perfeito': 1.0,
            'excelente': 0.9,
            'bom': 0.7,
            'gosto': 0.6,
            'terrivel': -1.0,
            'horrivel': -0.9,
            'ruim': -0.7,
            'odeio': -0.8,
            'problema': -0.6,
            'erro': -0.5,
        }
    
    def _load_intent_patterns(self) -> Dict[str, List[str]]:
        """Carrega padroes de intencao.
        
        Returns:
            Dicionario de intencoes e padroes
        """
        return {
            'saudacao': [r'ola', r'oi', r'bom dia', r'boa tarde', r'boa noite'],
            'despedida': [r'ate logo', r'tchau', r'adeus', r'falou'],
            'ajuda': [r'ajuda', r'socorro', r'como', r'pode me ajudar'],
            'confirmacao': [r'sim', r'yes', r'ok', r'beleza'],
            'negacao': [r'nao', r'no', r'nunca', r'jamais'],
        }
    
    def _load_stopwords(self) -> List[str]:
        """Carrega lista de stopwords em portugues.
        
        Returns:
            Lista de stopwords
        """
        return [
            'o', 'a', 'de', 'para', 'com', 'sem', 'por', 'e', 'ou',
            'que', 'qual', 'quando', 'onde', 'como', 'porque', 'nao',
            'um', 'uma', 'os', 'as', 'um', 'uma', 'ao', 'aos',
        ]
    
    def remove_stopwords(self, tokens: List[str]) -> List[str]:
        """Remove stopwords dos tokens.
        
        Args:
            tokens: Lista de tokens
            
        Returns:
            Tokens sem stopwords
        """
        return [t for t in tokens if t not in self.stopwords]
    
    def similarity(self, text1: str, text2: str) -> float:
        """Calcula similaridade entre dois textos.
        
        Args:
            text1: Primeiro texto
            text2: Segundo texto
            
        Returns:
            Score de similaridade (0-1)
        """
        tokens1 = set(self.tokenize(text1))
        tokens2 = set(self.tokenize(text2))
        
        if not tokens1 or not tokens2:
            return 0.0
        
        intersection = len(tokens1 & tokens2)
        union = len(tokens1 | tokens2)
        
        return intersection / union if union > 0 else 0.0
