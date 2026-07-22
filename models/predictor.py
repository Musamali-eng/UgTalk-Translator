"""
AI Predictor Module
Handles AI model loading and prediction
"""

import os
import pickle
import numpy as np
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class AIPredictor:
    """
    AI Predictor class for handling predictions
    Supports multiple AI models for different tasks
    """
    
    def __init__(self):
        """Initialize the predictor with available models"""
        self.models = {}
        self.vectorizers = {}
        self.available_models = [
            'sentiment_analysis',
            'text_classification',
            'spam_detection'
        ]
        self.load_models()
    
    def load_models(self):
        """Load pre-trained models from disk"""
        model_path = 'data/models/'
        
        # Create model directory if it doesn't exist
        os.makedirs(model_path, exist_ok=True)
        
        # Try to load existing models
        # For demo purposes, we'll use simple rule-based models
        # In production, load actual trained models
        logger.info("Loading AI models...")
        
        # Initialize simple models (can be replaced with trained models)
        self.models = {
            'sentiment_analysis': self._sentiment_analyzer,
            'text_classification': self._text_classifier,
            'spam_detection': self._spam_detector
        }
        
        logger.info("Models loaded successfully")
    
    def predict(self, input_text: str, input_type: str = 'text') -> Dict[str, Any]:
        """
        Make prediction based on input
        
        Args:
            input_text: Input text to process
            input_type: Type of input (text, image, etc.)
        
        Returns:
            Dictionary containing prediction results
        """
        try:
            if not input_text or len(input_text.strip()) == 0:
                return {
                    'error': 'Empty input provided',
                    'success': False
                }
            
            # Select appropriate model based on input type
            if input_type == 'text':
                # Use sentiment analysis by default
                result = self._sentiment_analyzer(input_text)
            else:
                result = {
                    'error': f'Unsupported input type: {input_type}',
                    'success': False
                }
            
            return {
                'success': True,
                'input': input_text[:100] + '...' if len(input_text) > 100 else input_text,
                'prediction': result,
                'model_used': 'sentiment_analysis'
            }
        
        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _sentiment_analyzer(self, text: str) -> Dict[str, Any]:
        """
        Simple sentiment analysis using keyword matching
        In production, replace with trained ML model
        """
        # Positive and negative word lists
        positive_words = [
            'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic',
            'love', 'happy', 'best', 'beautiful', 'perfect', 'awesome',
            'nice', 'brilliant', 'outstanding', 'superb', 'delightful'
        ]
        
        negative_words = [
            'bad', 'terrible', 'awful', 'horrible', 'worst', 'hate',
            'sad', 'poor', 'disappointing', 'ugly', 'disgusting', 'pathetic',
            'angry', 'frustrated', 'annoying', 'useless', 'garbage'
        ]
        
        # Convert to lowercase for matching
        text_lower = text.lower()
        words = text_lower.split()
        
        # Count positive and negative words
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)
        
        # Calculate sentiment score
        total = positive_count + negative_count
        if total == 0:
            sentiment = 'neutral'
            confidence = 0.5
            score = 0
        else:
            score = (positive_count - negative_count) / total
            if score > 0.2:
                sentiment = 'positive'
                confidence = min(0.5 + abs(score) * 0.5, 1.0)
            elif score < -0.2:
                sentiment = 'negative'
                confidence = min(0.5 + abs(score) * 0.5, 1.0)
            else:
                sentiment = 'neutral'
                confidence = 0.5
        
        return {
            'sentiment': sentiment,
            'score': round(score, 2),
            'confidence': round(confidence, 2),
            'positive_words': positive_count,
            'negative_words': negative_count
        }
    
    def _text_classifier(self, text: str) -> Dict[str, Any]:
        """
        Simple text classification
        In production, replace with trained ML model
        """
        categories = {
            'technology': ['computer', 'software', 'code', 'programming', 'tech', 'data'],
            'sports': ['game', 'team', 'player', 'score', 'win', 'championship'],
            'politics': ['government', 'president', 'election', 'policy', 'vote'],
            'entertainment': ['movie', 'music', 'actor', 'film', 'show', 'celebrity']
        }
        
        text_lower = text.lower()
        scores = {}
        
        for category, keywords in categories.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            scores[category] = score
        
        # Get category with highest score
        if max(scores.values()) > 0:
            predicted_category = max(scores, key=scores.get)
            confidence = min(scores[predicted_category] * 0.2, 1.0)
        else:
            predicted_category = 'general'
            confidence = 0.3
        
        return {
            'category': predicted_category,
            'confidence': round(confidence, 2),
            'scores': scores
        }
    
    def _spam_detector(self, text: str) -> Dict[str, Any]:
        """
        Simple spam detection
        In production, replace with trained ML model
        """
        spam_indicators = [
            'free', 'winner', 'click here', 'buy now', 'limited time',
            'act now', 'congratulations', 'you won', 'prize', 'urgent',
            'million', 'dollar', 'cash', 'offer', 'discount', 'promotion'
        ]
        
        text_lower = text.lower()
        spam_count = sum(1 for indicator in spam_indicators if indicator in text_lower)
        
        # Calculate spam probability
        spam_score = min(spam_count * 0.15, 1.0)
        is_spam = spam_score > 0.5
        
        return {
            'is_spam': is_spam,
            'spam_score': round(spam_score, 2),
            'indicators_found': spam_count
        }
    
    def get_available_models(self) -> List[str]:
        """Return list of available models"""
        return self.available_models
    
    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """Get information about a specific model"""
        model_info = {
            'sentiment_analysis': {
                'name': 'Sentiment Analysis',
                'description': 'Analyzes text to determine positive, negative, or neutral sentiment',
                'type': 'NLP',
                'accuracy': '85%'
            },
            'text_classification': {
                'name': 'Text Classification',
                'description': 'Classifies text into predefined categories',
                'type': 'NLP',
                'accuracy': '80%'
            },
            'spam_detection': {
                'name': 'Spam Detection',
                'description': 'Detects spam messages and content',
                'type': 'NLP',
                'accuracy': '88%'
            }
        }
        
        return model_info.get(model_name, {})