#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FastText Model Training Script - Week 4 Phase 2
Trains FastText models on Portuguese intent data for Agent-S NLP enhancement.
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Tuple, Optional

try:
    import fasttext
except ImportError:
    print("FastText not installed. Install with: pip install fasttext")
    sys.exit(1)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FastTextModelTrainer:
    """Trains FastText models for Portuguese intent classification."""
    
    def __init__(self, data_path: str = "train_intents.txt", model_dir: str = "models"):
        self.data_path = Path(data_path)
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(exist_ok=True)
        self.model_path = self.model_dir / "fasttext_intent_model.bin"
        self.vec_model_path = self.model_dir / "fasttext_vectors_model.bin"
        
    def prepare_training_data(self) -> bool:
        """Validate and prepare training data."""
        if not self.data_path.exists():
            logger.error(f"Training data not found: {self.data_path}")
            return False
        
        with open(self.data_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        logger.info(f"Loaded {len(lines)} training examples")
        return len(lines) > 0
    
    def train_supervised_model(self) -> Optional[fasttext.FastText._FastText]:
        """Train supervised FastText model for intent classification."""
        logger.info("Starting supervised FastText training...")
        
        try:
            model = fasttext.train_supervised(
                input=str(self.data_path),
                epoch=25,
                lr=0.5,
                wordNgrams=2,
                dim=100,
                minn=3,
                maxn=6,
                loss='softmax',
                verbose=2
            )
            
            model.save_model(str(self.model_path))
            logger.info(f"Model saved to {self.model_path}")
            
            # Print model info
            logger.info(f"Model labels: {model.get_labels()}")
            logger.info(f"Model vocabulary size: {len(model.get_words())}")
            
            return model
        except Exception as e:
            logger.error(f"Training failed: {str(e)}")
            return None
    
    def train_unsupervised_model(self) -> Optional[fasttext.FastText._FastText]:
        """Train unsupervised FastText model for word vectors."""
        logger.info("Starting unsupervised FastText training...")
        
        # Create text file for unsupervised training
        text_file = self.model_dir / "training_text.txt"
        with open(self.data_path, 'r', encoding='utf-8') as src:
            with open(text_file, 'w', encoding='utf-8') as dst:
                for line in src:
                    # Remove __label__ prefix
                    text = line.replace('__label__', '').strip()
                    dst.write(text + '\n')
        
        try:
            model = fasttext.train_unsupervised(
                input=str(text_file),
                epoch=10,
                lr=0.05,
                dim=100,
                minn=3,
                maxn=6,
                model='skipgram',
                ws=5,
                verbose=2
            )
            
            model.save_model(str(self.vec_model_path))
            logger.info(f"Vector model saved to {self.vec_model_path}")
            
            # Print model info
            logger.info(f"Vector model vocabulary size: {len(model.get_words())}")
            
            return model
        except Exception as e:
            logger.error(f"Vector model training failed: {str(e)}")
            return None
    
    def evaluate_model(self, model: fasttext.FastText._FastText) -> Tuple[float, float]:
        """Evaluate model performance on training data."""
        if not self.data_path.exists():
            return 0.0, 0.0
        
        N, loss = model.test(str(self.data_path))
        precision = model.test(str(self.data_path))[0] / N if N > 0 else 0.0
        
        logger.info(f"Model Evaluation - N: {N}, Loss: {loss}")
        return precision, loss
    
    def predict(self, model: fasttext.FastText._FastText, text: str, k: int = 1) -> Tuple[list, list]:
        """Make predictions on text."""
        predictions = model.predict(text, k=k)
        labels = [label.replace('__label__', '') for label in predictions[0]]
        confidences = predictions[1]
        return labels, confidences
    
    def run_training_pipeline(self) -> bool:
        """Run complete training pipeline."""
        logger.info("=" * 50)
        logger.info("FastText Model Training Pipeline - Week 4 Phase 2")
        logger.info("=" * 50)
        
        # Prepare data
        if not self.prepare_training_data():
            return False
        
        # Train supervised model
        sup_model = self.train_supervised_model()
        if sup_model:
            self.evaluate_model(sup_model)
        else:
            logger.warning("Supervised model training failed")
        
        # Train unsupervised model
        unsup_model = self.train_unsupervised_model()
        if unsup_model:
            logger.info("Unsupervised model training completed")
        else:
            logger.warning("Unsupervised model training failed")
        
        logger.info("=" * 50)
        logger.info("Training pipeline completed")
        logger.info("=" * 50)
        
        return sup_model is not None

if __name__ == "__main__":
    trainer = FastTextModelTrainer()
    success = trainer.run_training_pipeline()
    sys.exit(0 if success else 1)
