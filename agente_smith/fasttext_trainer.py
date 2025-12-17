#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FastText Model Trainer - Treinamento do modelo FastText
Week 4: Intent Classification ML Enhancement
"""

import fasttext
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

class FastTextTrainer:
    """
    Treina modelo FastText para classificação de intenções
    em comandos em português.
    """
    
    def __init__(self):
        self.model = None
        self.model_path = Path("models/intent_classifier.bin")
        self.training_data_path = Path("train_intents.txt")
        logger.info("FastText Trainer inicializado")
    
    def train(self, epochs: int = 25, lr: float = 1.0) -> bool:
        """
        Treina o modelo FastText.
        
        Args:
            epochs: Número de épocas de treinamento
            lr: Taxa de aprendizado
        
        Returns:
            True se treinamento bem-sucedido
        """
        try:
            if not self.training_data_path.exists():
                logger.error(f"Arquivo de treino não encontrado: {self.training_data_path}")
                return False
            
            logger.info(f"Iniciando treinamento FastText...")
            logger.info(f"- Dataset: {self.training_data_path}")
            logger.info(f"- Épocas: {epochs}")
            logger.info(f"- Taxa de aprendizado: {lr}")
            
            # Treina modelo
            self.model = fasttext.train_supervised(
                input=str(self.training_data_path),
                epoch=epochs,
                lr=lr,
                wordNgrams=2,
                dim=100,
                loss='softmax'
            )
            
            # Salva modelo
            self.model_path.parent.mkdir(parents=True, exist_ok=True)
            self.model.save_model(str(self.model_path))
            
            logger.info(f"Modelo treinado com sucesso!")
            logger.info(f"Salvo em: {self.model_path}")
            
            # Avalia modelo
            self._evaluate()
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao treinar modelo: {str(e)}")
            return False
    
    def _evaluate(self) -> None:
        """
        Avalia o desempenho do modelo.
        """
        try:
            if not self.model:
                return
            
            # Metrics
            N, P, R = self.model.test(str(self.training_data_path))
            
            logger.info(f"\n=== Métricas do Modelo ===")
            logger.info(f"Exemplos testados: {N}")
            logger.info(f"Precisão: {P:.4f}")
            logger.info(f"Recall: {R:.4f}")
            logger.info(f"F1 Score: {2*P*R/(P+R):.4f}")
            
        except Exception as e:
            logger.warning(f"Erro ao avaliar modelo: {str(e)}")
    
    def load_model(self) -> bool:
        """
        Carrega modelo existente.
        
        Returns:
            True se carregado com sucesso
        """
        try:
            if not self.model_path.exists():
                logger.error(f"Modelo não encontrado: {self.model_path}")
                return False
            
            self.model = fasttext.load_model(str(self.model_path))
            logger.info(f"Modelo carregado: {self.model_path}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao carregar modelo: {str(e)}")
            return False
    
    def predict(self, text: str, k: int = 1) -> Optional[tuple]:
        """
        Prediz intenção para um texto.
        
        Args:
            text: Texto para classificar
            k: Número de predições
        
        Returns:
            Tupla (labels, scores) ou None
        """
        try:
            if not self.model:
                logger.error("Modelo não carregado")
                return None
            
            labels, scores = self.model.predict(text, k=k)
            
            return labels, scores
            
        except Exception as e:
            logger.error(f"Erro ao fazer predição: {str(e)}")
            return None


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    trainer = FastTextTrainer()
    
    # Treina modelo
    if trainer.train():
        # Testa com alguns exemplos
        print("\n=== Testes de Predição ===")
        
        test_inputs = [
            "Abre o WhatsApp",
            "Fecha o Telegram",
            "Manda mensagem para João",
            "Liga para Maria",
            "Captura de tela"
        ]
        
        for text in test_inputs:
            result = trainer.predict(text)
            if result:
                labels, scores = result
                intent = labels[0].replace("__label__", "")
                score = float(scores[0])
                print(f"{text:30} → {intent:15} ({score:.1%})")
    else:
        print("Erro ao treinar modelo")
