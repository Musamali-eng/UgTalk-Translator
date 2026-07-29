"""
models/predictor.py - HYBRID Translation (ML + Dictionary)
ML tries first, Dictionary gives accurate results
"""

import os
import joblib
import re
import logging
import numpy as np
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class TranslationPredictor:
    """HYBRID Translation: ML from .pkl + Dictionary"""

    def __init__(self):
        self.is_loaded = False
        self.models = {}
        self.available_models = ['translation']
        
        # ML components
        self.vectorizer = None
        self.language_models = None
        self.le_language = None
        self.le_domain = None
        self.le_formality = None
        self.training_data = None
        self.ml_loaded = False
        
        # Load ML
        self._load_ml_models()
        
        # Load Dictionary (REAL translations)
        self._load_dictionary()
        
        self._init_models()

    def _load_ml_models(self):
        """Load ML from .pkl files"""
        try:
            model_dir = 'models/saved_models'
            self.vectorizer = joblib.load(f'{model_dir}/vectorizer.pkl')
            self.language_models = joblib.load(f'{model_dir}/language_models.pkl')
            self.le_language = joblib.load(f'{model_dir}/le_language.pkl')
            self.le_domain = joblib.load(f'{model_dir}/le_domain.pkl')
            self.le_formality = joblib.load(f'{model_dir}/le_formality.pkl')
            self.training_data = joblib.load(f'{model_dir}/training_data.pkl')
            self.ml_loaded = True
            print("✅ ML Model loaded from .pkl")
        except Exception as e:
            print(f"⚠️ ML not loaded: {e}")

    def _load_dictionary(self):
        """COMPLETE DICTIONARY - REAL TRANSLATIONS"""
        self.translations = {
            'Luganda': {
                # Greetings
                'good morning': 'Wasuze otya',
                'good afternoon': 'Osiibye otya',
                'good evening': 'Osiibye otya',
                'good night': 'Sula bulungi',
                'hello': 'Ki kati',
                'hi': 'Ki kati',
                'how are you': 'Oli otya',
                'i am fine': 'Ndi bulungi',
                'goodbye': 'Weeraba',
                'bye': 'Weeraba',
                'welcome': 'Tukusanyukidde',
                # Common phrases
                'thank you': 'Webale nnyo',
                'thanks': 'Webale',
                'yes': 'Yee',
                'no': 'Nedda',
                'please': 'Mwebale',
                'sorry': 'Nsonyiwa',
                'help': 'Nnyamba',
                'i love you': 'Nkwagala',
                'i miss you': 'Nkukwata',
                # Nouns
                'water': 'Amazzi',
                'food': 'Emmere',
                'hospital': 'Eddwaliro',
                'school': 'Essomero',
                'house': 'Ennyumba',
                'friend': 'Mukwano',
                'family': 'Amaka',
                'work': 'Omulimu',
                'home': 'Eka',
                'car': 'Emotoka',
                'phone': 'Essimu',
                # Time
                'today': 'Leero',
                'tomorrow': 'Nkya',
                'yesterday': 'Jjo',
                'morning': 'Makya',
                'afternoon': 'Akawungeezi',
                'evening': 'Akawungeezi',
                'night': 'Ekiro',
                # Actions
                'eat': 'Kulya',
                'drink': 'Kunywa',
                'sleep': 'Kwebaka',
                'good': 'Bulungi',
                'bad': 'Bibi',
                # Questions
                'what': 'Ki',
                'why': 'Lwaki',
                'where': 'Wa',
                'who': 'Ani',
                'how': 'Otya',
                # People
                'man': 'Omusajja',
                'woman': 'Omukazi',
                'child': 'Omwana',
                'father': 'Taata',
                'mother': 'Maama',
                'brother': 'Muganda',
                'sister': 'Muganda',
                'teacher': 'Omusomesa',
                'student': 'Omuyizi',
            },
            'Lusoga': {
                'good morning': 'Mirembe',
                'good afternoon': 'Osiibye otya',
                'good evening': 'Osiibye otya',
                'good night': 'Sula bulungi',
                'hello': 'Kale',
                'hi': 'Kale',
                'how are you': 'Oli otya',
                'i am fine': 'Ndi bulungi',
                'goodbye': 'Weeraba',
                'welcome': 'Tukusanyukidde',
                'thank you': 'Webale',
                'yes': 'Yee',
                'no': 'Nedda',
                'please': 'Mwebale',
                'sorry': 'Nsonyiwa',
                'help': 'Nnyamba',
                'i love you': 'Nkwagala',
                'water': 'Amazzi',
                'food': 'Emmere',
                'hospital': 'Eddwaliro',
                'school': 'Essomero',
                'house': 'Ennyumba',
                'friend': 'Mukwano',
                'today': 'Leero',
                'tomorrow': 'Nkya',
                'yesterday': 'Jjo',
                'good': 'Bulungi',
                'bad': 'Bibi',
                'eat': 'Kulya',
                'drink': 'Kunywa',
                'sleep': 'Kwebaka',
            },
            'Runyankole': {
                'good morning': 'Oraare gye',
                'good afternoon': 'Osiibye gye',
                'good evening': 'Osiibye gye',
                'good night': 'Siraare gye',
                'hello': 'Agandi',
                'hi': 'Agandi',
                'how are you': 'Oraare gye',
                'i am fine': 'Ndi mwe',
                'goodbye': 'Nimwe',
                'welcome': 'Tusiime',
                'thank you': 'Webale',
                'yes': 'Nee',
                'no': 'Ngangi',
                'please': 'Mwebale',
                'sorry': 'Nsonsiwe',
                'help': 'Nyanba',
                'i love you': 'Ninkukunda',
                'water': 'Amaizi',
                'food': 'Ekyokurya',
                'hospital': 'Erugaro',
                'school': 'Ishomero',
                'house': 'Enyumba',
                'friend': 'Mukwano',
                'good': 'Kurungi',
                'bad': 'Kubi',
                'eat': 'Kurya',
                'drink': 'Kunywa',
                'sleep': 'Kwebaka',
            },
            'Acholi': {
                'good morning': 'Itye nino',
                'good afternoon': 'Itye nino',
                'good evening': 'Itye nino',
                'good night': 'Otye maro',
                'hello': 'Yin kare',
                'hi': 'Yin kare',
                'how are you': 'Itye nino',
                'i am fine': 'Atye maber',
                'goodbye': 'Obedo maber',
                'welcome': 'Yin kare',
                'thank you': 'Apwoyo matek',
                'yes': 'Ee',
                'no': 'Pe',
                'please': 'Apwoyo',
                'sorry': 'Tim kica',
                'help': 'Konya',
                'i love you': 'Amaro ni',
                'water': 'Pii',
                'food': 'Camo',
                'hospital': 'Lac',
                'school': 'Sukul',
                'house': 'Ot',
                'friend': 'Onywal',
                'good': 'Maber',
                'bad': 'Rac',
                'eat': 'Camo',
                'drink': 'Mat',
                'sleep': 'Nind',
            },
            'Ateso': {
                'good morning': 'Itokei',
                'good afternoon': 'Aitokei',
                'good evening': 'Aitokei',
                'good night': 'Itokei nai',
                'hello': 'Ayo',
                'hi': 'Ayo',
                'how are you': 'Itokei',
                'i am fine': 'Ito nai',
                'goodbye': 'Nayai',
                'welcome': 'Kale',
                'thank you': 'Eyalama',
                'yes': 'Ee',
                'no': 'Mam',
                'please': 'Eyalama',
                'sorry': 'Naya',
                'help': 'Konya',
                'i love you': 'Eong amaritai',
                'water': 'Akwam',
                'food': 'Ekyek',
                'hospital': 'Adug',
                'school': 'Sukul',
                'house': 'Eot',
                'friend': 'Nyek',
                'good': 'Nai',
                'bad': 'Adug',
                'eat': 'Akinyam',
                'drink': 'Akimat',
                'sleep': 'Akisak',
            },
            'Lugbara': {
                'good morning': 'Molo',
                'good afternoon': 'Molo',
                'good evening': 'Molo',
                'good night': 'Oru',
                'hello': 'Molo',
                'hi': 'Molo',
                'how are you': 'Molo',
                'i am fine': 'Molo nza',
                'goodbye': 'Oru',
                'welcome': 'Wuruke',
                'thank you': 'Mvolo',
                'yes': 'Ee',
                'no': 'Awa',
                'please': 'Mvolo',
                'sorry': 'Mvolo',
                'help': 'Konya',
                'i love you': 'Ma ti',
                'water': 'Iyi',
                'food': 'Ekye',
                'hospital': 'Adu',
                'school': 'Sukul',
                'house': 'Eot',
                'friend': 'Nyek',
                'good': 'Nza',
                'bad': 'Adu',
                'eat': 'Ekye',
                'drink': 'Iyi',
                'sleep': 'Oru',
            },
            'Rukiga': {
                'good morning': 'Oraare gye',
                'good afternoon': 'Osiibye gye',
                'good evening': 'Osiibye gye',
                'good night': 'Siraare gye',
                'hello': 'Agandi',
                'hi': 'Agandi',
                'how are you': 'Oraare gye',
                'i am fine': 'Ndi mwe',
                'goodbye': 'Nimwe',
                'welcome': 'Tusiime',
                'thank you': 'Webale',
                'yes': 'Nee',
                'no': 'Ngangi',
                'please': 'Mwebale',
                'sorry': 'Nsonsiwe',
                'help': 'Nyanba',
                'i love you': 'Ninkukunda',
                'water': 'Amaizi',
                'food': 'Ekyokurya',
                'hospital': 'Erugaro',
                'school': 'Ishomero',
                'house': 'Enyumba',
                'friend': 'Mukwano',
                'good': 'Kurungi',
                'bad': 'Kubi',
                'eat': 'Kurya',
                'drink': 'Kunywa',
                'sleep': 'Kwebaka',
            }
        }
        print(f"✅ Dictionary loaded: {len(self.translations)} languages")

    def _init_models(self):
        """Initialize models"""
        self.models = {
            'translation': self.translate
        }
        self.is_loaded = True

    def _clean_text(self, text: str) -> str:
        """Clean input text"""
        if not isinstance(text, str):
            text = str(text)
        text = text.lower().strip()
        text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
        return text

    def get_languages(self) -> List[str]:
        """Get supported languages"""
        return list(self.translations.keys())

    def get_domains(self) -> List[str]:
        """Get supported domains"""
        return ['Daily Conversation', 'Health', 'Tourism', 'Education', 'Business', 'Agriculture', 'Government']

    def get_formality_levels(self) -> List[str]:
        """Get formality levels"""
        return ['Formal', 'Informal']

    def get_stats(self) -> Dict[str, Any]:
        """Get model statistics"""
        return {
            'status': 'loaded',
            'languages': len(self.get_languages()),
            'domains': 7,
            'formality_levels': 2,
            'model_type': 'HYBRID (ML + Dictionary)',
            'ml_loaded': self.ml_loaded
        }

    def _dictionary_translate(self, text: str, target_language: str) -> Dict[str, Any]:
        """Translate using dictionary (RELIABLE)"""
        if target_language not in self.translations:
            return None
        
        cleaned = self._clean_text(text)
        lang_dict = self.translations[target_language]
        
        # Exact match
        if cleaned in lang_dict:
            return {
                'success': True,
                'original': text,
                'translation': lang_dict[cleaned],
                'target_language': target_language,
                'domain': 'Dictionary',
                'formality': 'Informal',
                'confidence': 1.0,
                'model_used': 'Dictionary (Exact)'
            }
        
        # Partial match
        best_match = None
        best_score = 0
        for key, value in lang_dict.items():
            if key in cleaned or cleaned in key:
                score = len(key) / max(len(cleaned), 1)
                if score > best_score:
                    best_score = score
                    best_match = value
        
        if best_match and best_score > 0.2:
            return {
                'success': True,
                'original': text,
                'translation': best_match,
                'target_language': target_language,
                'domain': 'Dictionary',
                'formality': 'Informal',
                'confidence': min(0.8, best_score + 0.2),
                'model_used': 'Dictionary (Partial)'
            }
        
        # Word-by-word
        words = cleaned.split()
        translated = []
        found = False
        for word in words:
            word_clean = re.sub(r'[^a-zA-Z]', '', word)
            if word_clean in lang_dict:
                translated.append(lang_dict[word_clean])
                found = True
            else:
                translated.append(word)
        
        if found:
            return {
                'success': True,
                'original': text,
                'translation': ' '.join(translated),
                'target_language': target_language,
                'domain': 'Dictionary',
                'formality': 'Informal',
                'confidence': 0.5,
                'model_used': 'Dictionary (Word-by-Word)'
            }
        
        return None

    def translate(self, text: str, target_language: str, domain: str = None, formality: str = None) -> Dict[str, Any]:
        """HYBRID Translation: Dictionary FIRST (RELIABLE)"""
        if not text or not text.strip():
            return {'success': False, 'error': 'Please enter text to translate'}

        text = text.strip()
        
        if target_language not in self.translations:
            return {
                'success': False,
                'error': f'Language "{target_language}" not supported. Available: {list(self.translations.keys())}'
            }

        # Dictionary FIRST (reliable)
        dict_result = self._dictionary_translate(text, target_language)
        if dict_result:
            return dict_result

        # ML as fallback (if dictionary fails)
        if self.ml_loaded:
            try:
                cleaned = self._clean_text(text)
                text_vector = self.vectorizer.transform([cleaned])
                lang_model = self.language_models[target_language]
                distances, indices = lang_model['model'].kneighbors(text_vector)
                
                best_idx = indices[0][0]
                if best_idx < len(lang_model['texts']):
                    translation = lang_model['texts'][best_idx]
                    # Only use ML if result isn't the same as input
                    if translation.lower() != text.lower():
                        return {
                            'success': True,
                            'original': text,
                            'translation': translation,
                            'target_language': target_language,
                            'domain': lang_model['domains'][best_idx],
                            'formality': lang_model['formality'][best_idx],
                            'confidence': float(1 - distances[0][0]),
                            'model_used': 'ML (Nearest Neighbors)'
                        }
            except Exception as e:
                pass

        return {
            'success': False,
            'error': f'Could not translate "{text}" to {target_language}.'
        }


AIPredictor = TranslationPredictor


if __name__ == "__main__":
    predictor = TranslationPredictor()
    print("=" * 70)
    print("🧪 TRANSLATION TEST")
    print("=" * 70)
    
    print(f"\n📊 Languages: {predictor.get_languages()}")
    
    tests = [
        ("thank you", "Luganda"),
        ("good morning", "Luganda"),
        ("how are you", "Luganda"),
        ("drinking water", "Luganda"),
        ("some drinking water", "Luganda"),
        ("I love you", "Luganda"),
        ("good morning my friend", "Luganda"),
    ]
    
    print("\n📊 Results:")
    print("-" * 60)
    for text, lang in tests:
        result = predictor.translate(text, lang)
        if result.get('success'):
            print(f"✅ '{text}' → {lang}: {result['translation']}")
            print(f"   Model: {result.get('model_used', 'Unknown')}")
            print(f"   Confidence: {result.get('confidence', 'N/A')}")
        else:
            print(f"❌ '{text}' → {lang}: {result.get('error')}")
        print()