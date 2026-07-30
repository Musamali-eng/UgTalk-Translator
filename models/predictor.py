"""
models/predictor.py - PURE ML Translation
Uses ONLY .pkl models trained from CSV dataset.
"""

import os
import joblib
import re
import numpy as np
from typing import Dict, Any, List

class TranslationPredictor:
    """
    PURE ML Translation - Uses ONLY .pkl models from CSV!
    
    This predictor loads trained machine learning models from .pkl files
    that were trained on the Language Translation CSV dataset.
    No hardcoded translations or dictionary fallback is used.
    """
    
    def __init__(self):
        """Initialize the predictor with empty model components."""
        self.is_loaded = False
        self.models = {}
        self.available_models = ['translation']
        
        # ML components loaded from .pkl files (trained on CSV)
        self.vectorizer = None          # TF-IDF vectorizer from training
        self.language_models = None     # Nearest Neighbors models per language
        self.le_language = None         # Label encoder for languages
        self.le_domain = None           # Label encoder for domains
        self.le_formality = None        # Label encoder for formality
        self.training_data = None       # Original training data
        
        self._load_models()
        self._init_models()

    def _load_models(self):
        """
        Load PURE ML models from .pkl files.
        These files were created during Jupyter notebook training.
        """
        try:
            model_dir = 'models/saved_models'
            
            # List of required model files
            required_files = [
                'vectorizer.pkl',       # TF-IDF vectorizer
                'language_models.pkl',  # Nearest Neighbors models
                'le_language.pkl',      # Language encoder
                'le_domain.pkl',        # Domain encoder
                'le_formality.pkl',     # Formality encoder
                'training_data.pkl'     # Training data reference
            ]
            
            # Check if all required files exist
            for f in required_files:
                if not os.path.exists(os.path.join(model_dir, f)):
                    print(f" Missing: {f}")
                    return
            
            # Load all .pkl files
            self.vectorizer = joblib.load(f'{model_dir}/vectorizer.pkl')
            self.language_models = joblib.load(f'{model_dir}/language_models.pkl')
            self.le_language = joblib.load(f'{model_dir}/le_language.pkl')
            self.le_domain = joblib.load(f'{model_dir}/le_domain.pkl')
            self.le_formality = joblib.load(f'{model_dir}/le_formality.pkl')
            self.training_data = joblib.load(f'{model_dir}/training_data.pkl')
            
            print(f"PURE ML loaded from CSV: {len(self.language_models)} languages")
            
        except Exception as e:
            print(f" Error loading models: {e}")

    def _init_models(self):
        """Initialize the available models dictionary."""
        self.models = {'translation': self.translate}
        self.is_loaded = self.vectorizer is not None

    def _clean_text(self, text: str) -> str:
        """
        Clean input text to match training data format.
        
        Args:
            text: Raw input text from user
            
        Returns:
            Cleaned text for vectorization
        """
        if not isinstance(text, str):
            text = str(text)
        text = text.lower().strip()           # Convert to lowercase
        text = re.sub(r'[^a-zA-Z0-9\s]', '', text)  # Remove special characters
        return text

    def get_languages(self) -> List[str]:
        """
        Get list of supported languages from the trained model.
        
        Returns:
            List of language names
        """
        if self.le_language is not None:
            return self.le_language.classes_.tolist()
        return []

    def get_domains(self) -> List[str]:
        """
        Get list of supported domains from the trained model.
        
        Returns:
            List of domain names
        """
        if self.le_domain is not None:
            return self.le_domain.classes_.tolist()
        return []

    def get_formality_levels(self) -> List[str]:
        """
        Get list of formality levels from the trained model.
        
        Returns:
            List of formality levels
        """
        if self.le_formality is not None:
            return self.le_formality.classes_.tolist()
        return []

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the loaded model.
        
        Returns:
            Dictionary with model information
        """
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
            'model_type': 'PURE ML (TF-IDF + Nearest Neighbors)',
            'source': 'CSV Dataset'
        }

    def translate(self, text: str, target_language: str, domain: str = None, formality: str = None) -> Dict[str, Any]:
        """
        PURE ML TRANSLATION - Uses ONLY .pkl models from CSV!
        
        This method performs translation using the trained ML model.
        NO dictionary lookups are used - everything comes from the model.
        
        Args:
            text: English text to translate
            target_language: Target Ugandan language
            domain: Optional domain filter
            formality: Optional formality filter
            
        Returns:
            Dictionary with translation result and metadata
        """
        # Check if model is loaded
        if not self.is_loaded:
            return {
                'success': False, 
                'error': 'ML Model not loaded. Please train the model first.'
            }

        # Validate input
        if not text or not text.strip():
            return {'success': False, 'error': 'Please enter text to translate'}

        text = text.strip()
        
        # Check if target language exists in model
        if target_language not in self.language_models:
            return {
                'success': False,
                'error': f'Language "{target_language}" not supported. Available: {list(self.language_models.keys())}'
            }

        try:
            # Step 1: Clean the input text
            cleaned_text = self._clean_text(text)
            
            if not cleaned_text:
                return {'success': False, 'error': 'Invalid input text'}
            
            # Step 2: Vectorize using TF-IDF (from CSV training)
            text_vector = self.vectorizer.transform([cleaned_text])
            
            # Step 3: Get the language model (from CSV training)
            lang_model = self.language_models[target_language]
            
            # Step 4: ML: Find nearest translations using Nearest Neighbors
            distances, indices = lang_model['model'].kneighbors(text_vector)
            
            # Step 5: Get the best match from ML model
            best_idx = indices[0][0]
            
            if best_idx < len(lang_model['texts']):
                # PURE ML - translation comes from CSV-trained model!
                return {
                    'success': True,
                    'original': text,
                    'translation': lang_model['texts'][best_idx],
                    'target_language': target_language,
                    'domain': lang_model['domains'][best_idx],
                    'formality': lang_model['formality'][best_idx],
                    'confidence': round(float(1 - distances[0][0]), 3),
                    'model_used': 'PURE ML (Nearest Neighbors + TF-IDF)',
                    'source': 'CSV Dataset',
                    'similar_text': lang_model['sources'][best_idx]
                }
            
            # No translation found
            return {
                'success': False,
                'error': f'No translation found for "{text}" in {target_language}.'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Translation error: {str(e)}'
            }


# For backwards compatibility with existing code
AIPredictor = TranslationPredictor