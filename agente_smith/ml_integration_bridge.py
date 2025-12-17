#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ML Integration Bridge - Week 4 Phase 2
Integrates FastText models with NLPCommandBridge for enhanced intent recognition.
"""

import os
import sys
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional

try:
    import fasttext
except ImportError:
    fasttext = None

logger = logging.getLogger(__name__)

class MLIntegrationBridge:
    """Bridges FastText models with NLP command processing."""
    
    def __init__(self, model_dir: str = "models"):
        self.model_dir = Path(model_dir)
        self.supervised_model = None
        self.unsupervised_model = None
        self.confidence_threshold = 0.6
        self.load_models()
    
    def load_models(self) -> bool:
        """Load trained FastText models."""
        if not fasttext:
            logger.warning("FastText not available")
            return False
        
        sup_model_path = self.model_dir / "fasttext_intent_model.bin"
        unsup_model_path = self.model_dir / "fasttext_vectors_model.bin"
        
        try:
            if sup_model_path.exists():
                self.supervised_model = fasttext.load_model(str(sup_model_path))
                logger.info(f"Loaded supervised model: {sup_model_path}")
            
            if unsup_model_path.exists():
                self.unsupervised_model = fasttext.load_model(str(unsup_model_path))
                logger.info(f"Loaded unsupervised model: {unsup_model_path}")
            
            return self.supervised_model is not None
        except Exception as e:
            logger.error(f"Failed to load models: {str(e)}")
            return False
    
    def classify_intent(self, text: str, k: int = 3) -> List[Tuple[str, float]]:
        """Classify text intent using FastText supervised model."""
        if not self.supervised_model:
            return []
        
        try:
            predictions = self.supervised_model.predict(text, k=k)
            results = []
            
            for label, confidence in zip(predictions[0], predictions[1]):
                clean_label = label.replace('__label__', '')
                if confidence >= self.confidence_threshold:
                    results.append((clean_label, float(confidence)))
            
            return results
        except Exception as e:
            logger.error(f"Intent classification failed: {str(e)}")
            return []
    
    def get_word_vectors(self, word: str) -> Optional[List[float]]:
        """Get word vector from unsupervised model."""
        if not self.unsupervised_model:
            return None
        
        try:
            vector = self.unsupervised_model.get_word_vector(word)
            return vector.tolist() if hasattr(vector, 'tolist') else list(vector)
        except Exception as e:
            logger.error(f"Vector retrieval failed: {str(e)}")
            return None
    
    def compute_text_similarity(self, text1: str, text2: str) -> float:
        """Compute similarity between two texts using word vectors."""
        if not self.unsupervised_model:
            return 0.0
        
        try:
            vec1 = self.unsupervised_model.get_sentence_vector(text1)
            vec2 = self.unsupervised_model.get_sentence_vector(text2)
            
            # Cosine similarity
            import numpy as np
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return float(dot_product / (norm1 * norm2))
        except Exception as e:
            logger.error(f"Similarity computation failed: {str(e)}")
            return 0.0
    
    def enhance_nlp_processing(self, text: str) -> Dict:
        """Enhance NLP processing with ML models."""
        result = {
            'original_text': text,
            'intents': self.classify_intent(text),
            'primary_intent': None,
            'confidence': 0.0,
            'enhanced': False
        }
        
        if result['intents']:
            primary_intent, confidence = result['intents'][0]
            result['primary_intent'] = primary_intent
            result['confidence'] = confidence
            result['enhanced'] = True
        
        return result
    
    def batch_classify(self, texts: List[str]) -> List[Dict]:
        """Classify multiple texts."""
        return [self.enhance_nlp_processing(text) for text in texts]
    
    def set_confidence_threshold(self, threshold: float):
        """Set minimum confidence threshold for classifications."""
        self.confidence_threshold = max(0.0, min(1.0, threshold))
        logger.info(f"Confidence threshold set to {self.confidence_threshold}")

def integrate_with_nlp_bridge(nlp_bridge, ml_bridge: MLIntegrationBridge) -> None:
    """Integrate ML bridge with existing NLP command bridge."""
    """Requires ml_enhanced_nlp.py integration."""
    logger.info("ML Integration Bridge initialized and ready for NLP pipeline integration")

if __name__ == "__main__":
    bridge = MLIntegrationBridge()
    
    # Test classification
    test_texts = [
        "ligar o ar condicionado na sala",
        "qual é a temperatura atual",
        "reproduzir música de piano"
    ]
    
    for text in test_texts:
        result = bridge.enhance_nlp_processing(text)
        print(f"Text: {text}")
        print(f"Result: {result}")
        print()
