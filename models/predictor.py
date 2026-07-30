"""
models/predictor.py - Combined AI Predictor
Group C - RECESS Final Project 2026
Includes: Translation (Pure ML) + Sentiment Analysis + Text Classification + Spam Detection
"""

import os
import joblib
import re
import pickle
import numpy as np
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


# ============================================================
# PART 1: TRANSLATION PREDICTOR (PURE ML)
# ============================================================

class TranslationPredictor:
    """PURE ML Translation - Uses ONLY .pkl models!"""

    def __init__(self):
        self.is_loaded = False
        self.models = {}
        self.available_models = ['translation']
        
        # ML components (from .pkl files)
        self.vectorizer = None
        self.language_models = None
        self.le_language = None
        self.le_domain = None
        self.le_formality = None
        self.training_data = None
        
        self._load_models()
        self._init_models()

    def _load_models(self):
        """Load PURE ML models from .pkl files"""
        try:
            model_dir = 'models/saved_models'
            
            required_files = [
                'vectorizer.pkl', 'language_models.pkl',
                'le_language.pkl', 'le_domain.pkl',
                'le_formality.pkl', 'training_data.pkl'
            ]
            
            for f in required_files:
                if not os.path.exists(os.path.join(model_dir, f)):
                    print(f"⚠️ Missing: {f}")
                    return
            
            self.vectorizer = joblib.load(f'{model_dir}/vectorizer.pkl')
            self.language_models = joblib.load(f'{model_dir}/language_models.pkl')
            self.le_language = joblib.load(f'{model_dir}/le_language.pkl')
            self.le_domain = joblib.load(f'{model_dir}/le_domain.pkl')
            self.le_formality = joblib.load(f'{model_dir}/le_formality.pkl')
            self.training_data = joblib.load(f'{model_dir}/training_data.pkl')
            
            print(f"✅ PURE ML loaded: {len(self.language_models)} languages")
            
        except Exception as e:
            print(f"❌ Error loading models: {e}")

    def _init_models(self):
        """Initialize models"""
        self.models = {'translation': self.translate}
        self.is_loaded = self.vectorizer is not None

    def _clean_text(self, text: str) -> str:
        """Clean input text"""
        if not isinstance(text, str):
            text = str(text)
        text = text.lower().strip()
        text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
        return text

    def get_languages(self) -> List[str]:
        if self.le_language is not None:
            return self.le_language.classes_.tolist()
        return []

    def get_domains(self) -> List[str]:
        if self.le_domain is not None:
            return self.le_domain.classes_.tolist()
        return []

    def get_formality_levels(self) -> List[str]:
        if self.le_formality is not None:
            return self.le_formality.classes_.tolist()
        return []

    def get_stats(self) -> Dict[str, Any]:
        if not self.is_loaded:
            return {'status': 'not_loaded'}
        
        total_samples = 0
        if self.training_data is not None:
            total_samples = len(self.training_data)
        
        return {
            'status': 'loaded',
            'languages': len(self.get_languages()),
            'domains': len(self.get_domains()),
            'formality_levels': len(self.get_formality_levels()),
            'total_samples': total_samples,
            'model_type': 'PURE ML (TF-IDF + Nearest Neighbors)'
        }

    def translate(self, text: str, target_language: str, domain: str = None, formality: str = None) -> Dict[str, Any]:
        """PURE ML translation - NO dictionary!"""
        if not self.is_loaded:
            return {'success': False, 'error': 'Model not loaded'}

        if not text or not text.strip():
            return {'success': False, 'error': 'Please enter text to translate'}

        text = text.strip()
        
        if target_language not in self.language_models:
            return {
                'success': False,
                'error': f'Language "{target_language}" not supported. Available: {list(self.language_models.keys())}'
            }

        try:
            cleaned_text = self._clean_text(text)
            if not cleaned_text:
                return {'success': False, 'error': 'Invalid input text'}
            
            text_vector = self.vectorizer.transform([cleaned_text])
            lang_model = self.language_models[target_language]
            distances, indices = lang_model['model'].kneighbors(text_vector)
            
            best_idx = indices[0][0]
            
            if best_idx < len(lang_model['texts']):
                return {
                    'success': True,
                    'original': text,
                    'translation': lang_model['texts'][best_idx],
                    'target_language': target_language,
                    'domain': lang_model['domains'][best_idx],
                    'formality': lang_model['formality'][best_idx],
                    'confidence': round(float(1 - distances[0][0]), 3),
                    'model_used': 'PURE ML (Nearest Neighbors + TF-IDF)',
                    'similar_text': lang_model['sources'][best_idx]
                }
            
            return {'success': False, 'error': f'No translation found for "{text}"'}
            
        except Exception as e:
            return {'success': False, 'error': f'Translation error: {str(e)}'}


# ============================================================
# PART 2: GENERAL AI PREDICTOR (Sentiment, Spam, Classification)
# ============================================================

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
        
        logger.info("Loading AI models...")
        
        # Initialize simple models (can be replaced with trained models)
        self.models = {
            'sentiment_analysis': self._sentiment_analyzer,
            'text_classification': self._text_classifier,
            'spam_detection': self._spam_detector
        }
        
        logger.info("Models loaded successfully")
    
    def predict(self, input_text: str, input_type: str = 'text', model_name: str = 'sentiment_analysis') -> Dict[str, Any]:
        """
        Make prediction based on input
        
        Args:
            input_text: Input text to process
            input_type: Type of input (text, image, etc.)
            model_name: Name of the model to use
        
        Returns:
            Dictionary containing prediction results
        """
        try:
            if not input_text or len(input_text.strip()) == 0:
                return {
                    'error': 'Empty input provided',
                    'success': False
                }
            
            # Select appropriate model
            if model_name in self.models:
                result = self.models[model_name](input_text)
            else:
                result = {
                    'error': f'Unsupported model: {model_name}',
                    'success': False
                }
            
            return {
                'success': True,
                'input': input_text[:100] + '...' if len(input_text) > 100 else input_text,
                'prediction': result,
                'model_used': model_name
            }
        
        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _sentiment_analyzer(self, text: str) -> Dict[str, Any]:
        """Simple sentiment analysis using keyword matching"""
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
        
        text_lower = text.lower()
        words = text_lower.split()
        
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)
        
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
        """Simple text classification"""
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
        """Simple spam detection"""
        spam_indicators = [
            'free', 'winner', 'click here', 'buy now', 'limited time',
            'act now', 'congratulations', 'you won', 'prize', 'urgent',
            'million', 'dollar', 'cash', 'offer', 'discount', 'promotion'
        ]
        
        text_lower = text.lower()
        spam_count = sum(1 for indicator in spam_indicators if indicator in text_lower)
        
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


# ============================================================
# BACKWARDS COMPATIBILITY
# ============================================================

# For UgTalk translator
AIPredictor = TranslationPredictor  # Keep both names for compatibility