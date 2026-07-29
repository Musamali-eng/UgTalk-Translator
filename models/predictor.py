"""
models/predictor.py - PURE ML Translation
Uses ONLY .pkl models trained on the dataset. NO dictionary!
"""

import os
import joblib
import re
from typing import Dict, Any, List

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
                    print(f" Missing: {f}")
                    return
            
            self.vectorizer = joblib.load(f'{model_dir}/vectorizer.pkl')
            self.language_models = joblib.load(f'{model_dir}/language_models.pkl')
            self.le_language = joblib.load(f'{model_dir}/le_language.pkl')
            self.le_domain = joblib.load(f'{model_dir}/le_domain.pkl')
            self.le_formality = joblib.load(f'{model_dir}/le_formality.pkl')
            self.training_data = joblib.load(f'{model_dir}/training_data.pkl')
            
            print(f"PURE ML loaded: {len(self.language_models)} languages")
            
        except Exception as e:
            print(f"❌ Error: {e}")

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
        
        # FIX: Check if training_data is not None, then get length
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


AIPredictor = TranslationPredictor


if __name__ == "__main__":
    predictor = TranslationPredictor()
    print("=" * 60)
    print(" PURE ML TRANSLATION TEST")
    print("=" * 60)
    
    if not predictor.is_loaded:
        print("Model not loaded. Run Jupyter notebook first.")
        exit()
    
    print(f"\n Languages: {predictor.get_languages()}")
    print(f" Samples: {predictor.get_stats()['total_samples']}")
    
    tests = ["Thank you", "Good morning", "I love you", "drinking water"]
    
    for text in tests:
        result = predictor.translate(text, "Luganda")
        if result.get('success'):
            print(f"\n '{text}' → {result['translation']}")
            print(f"   Confidence: {result['confidence']:.2%}")
        else:
            print(f"\n'{text}' → {result.get('error')}")