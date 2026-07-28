"""
models/predictor.py - Translation with REAL Dictionary + Word-by-Word
"""

import os
import json
import re
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class TranslationPredictor:
    """Translation predictor using dictionary with word-by-word fallback"""

    def __init__(self):
        self.is_loaded = False
        self.models = {}
        self.available_models = ['translation']
        self.translations = {}
        self._load_translations()
        self._init_models()

    def _load_translations(self):
        """Load REAL translations from JSON"""
        try:
            possible_paths = [
                'models/saved_models/translations.json',
                '../models/saved_models/translations.json',
                'translations.json',
                os.path.join(os.path.dirname(__file__), 'saved_models', 'translations.json')
            ]
            
            json_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    json_path = path
                    break
            
            if json_path:
                with open(json_path, 'r', encoding='utf-8') as f:
                    self.translations = json.load(f)
                print(f"✅ Loaded translations from: {json_path}")
                print(f"   Languages: {len(self.translations)}")
                print(f"   Languages: {list(self.translations.keys())}")
            else:
                print(f"❌ translations.json not found!")
                self._create_fallback_translations()
                
        except Exception as e:
            print(f"❌ Error loading translations: {e}")
            self._create_fallback_translations()

    def _create_fallback_translations(self):
        """Create fallback translations if file missing"""
        self.translations = {
            'Luganda': {
                'good morning': 'Wasuze otya',
                'thank you': 'Webale nnyo',
                'welcome': 'Tukusanyukidde',
                'hello': 'Ki kati',
                'how are you': 'Oli otya',
                'i love you': 'Nkwagala',
                'water': 'Amazzi',
                'food': 'Emmere',
                'hospital': 'Eddwaliro',
                'school': 'Essomero',
                'house': 'Ennyumba',
                'friend': 'Mukwano',
                'today': 'Leero',
                'tomorrow': 'Nkya',
                'good': 'Bulungi',
                'bad': 'Bibi',
                'eat': 'Kulya',
                'drink': 'Kunywa',
                'sleep': 'Kwebaka',
                'work': 'Omulimu',
                'home': 'Eka',
                'car': 'Emotoka',
                'phone': 'Essimu',
            },
            'Lusoga': {
                'good morning': 'Mirembe',
                'thank you': 'Webale',
                'welcome': 'Tukusanyukidde',
                'hello': 'Kale',
                'how are you': 'Oli otya',
                'i love you': 'Nkwagala',
                'water': 'Amazzi',
                'food': 'Emmere',
                'hospital': 'Eddwaliro',
                'school': 'Essomero',
                'house': 'Ennyumba',
                'friend': 'Mukwano',
                'today': 'Leero',
                'tomorrow': 'Nkya',
                'good': 'Bulungi',
                'bad': 'Bibi',
                'eat': 'Kulya',
                'drink': 'Kunywa',
                'sleep': 'Kwebaka',
            },
            'Runyankole': {
                'good morning': 'Oraare gye',
                'thank you': 'Webale',
                'welcome': 'Tusiime',
                'hello': 'Agandi',
                'how are you': 'Oraare gye',
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
                'thank you': 'Apwoyo matek',
                'welcome': 'Yin kare',
                'hello': 'Yin kare',
                'how are you': 'Itye nino',
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
                'thank you': 'Eyalama',
                'welcome': 'Kale',
                'hello': 'Ayo',
                'how are you': 'Itokei',
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
                'thank you': 'Mvolo',
                'welcome': 'Wuruke',
                'hello': 'Molo',
                'how are you': 'Molo',
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
                'thank you': 'Webale',
                'welcome': 'Tusiime',
                'hello': 'Agandi',
                'how are you': 'Oraare gye',
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
        print("⚠️ Using fallback translations (7 languages)")

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
            'model_type': 'Dictionary Translation'
        }

    def translate(self, text: str, target_language: str, domain: str = None, formality: str = None) -> Dict[str, Any]:
        """Translate text using dictionary + word-by-word fallback"""
        if not text or not text.strip():
            return {'success': False, 'error': 'Please enter text to translate'}

        text = text.strip()
        cleaned = self._clean_text(text)
        
        if target_language not in self.translations:
            return {
                'success': False,
                'error': f'Language "{target_language}" not supported. Available: {list(self.translations.keys())}'
            }

        lang_dict = self.translations[target_language]
        
        # STEP 1: Exact match
        if cleaned in lang_dict:
            return {
                'success': True,
                'original': text,
                'translation': lang_dict[cleaned],
                'target_language': target_language,
                'domain': 'Dictionary',
                'formality': 'Informal',
                'confidence': 1.0,
                'model_used': 'Dictionary (Exact Match)'
            }
        
        # STEP 2: Partial match
        for key, value in lang_dict.items():
            if key in cleaned or cleaned in key:
                return {
                    'success': True,
                    'original': text,
                    'translation': value,
                    'target_language': target_language,
                    'domain': 'Dictionary',
                    'formality': 'Informal',
                    'confidence': 0.8,
                    'model_used': 'Dictionary (Partial Match)'
                }
        
        # STEP 3: Word-by-word translation (NEW!)
        words = cleaned.split()
        translated_words = []
        found_any = False
        
        for word in words:
            # Remove punctuation
            word_clean = re.sub(r'[^a-zA-Z]', '', word)
            if word_clean in lang_dict:
                translated_words.append(lang_dict[word_clean])
                found_any = True
            else:
                # Keep original word if not found
                translated_words.append(word)
        
        if found_any:
            return {
                'success': True,
                'original': text,
                'translation': ' '.join(translated_words),
                'target_language': target_language,
                'domain': 'Dictionary',
                'formality': 'Informal',
                'confidence': 0.6,
                'model_used': 'Dictionary (Word-by-Word)'
            }

        # STEP 4: No translation found
        return {
            'success': False,
            'error': f'Could not translate "{text}" to {target_language}. Try a shorter phrase.'
        }

    def predict(self, text: str) -> Dict[str, Any]:
        """Make prediction on input text"""
        if not text or not text.strip():
            return {'success': False, 'error': 'Empty input'}

        positive = {'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 
                   'love', 'happy', 'best', 'beautiful', 'perfect', 'awesome', 'nice'}
        negative = {'bad', 'terrible', 'awful', 'horrible', 'worst', 'hate', 
                   'sad', 'poor', 'disappointing', 'ugly', 'angry'}

        words = text.lower().split()
        pos_count = sum(1 for w in words if w in positive)
        neg_count = sum(1 for w in words if w in negative)
        total = pos_count + neg_count

        if total == 0:
            sentiment = 'neutral'
            confidence = 0.5
        else:
            score = (pos_count - neg_count) / total
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
            'success': True,
            'prediction': {
                'sentiment': sentiment,
                'confidence': confidence
            },
            'model_used': 'sentiment_analysis'
        }


AIPredictor = TranslationPredictor


if __name__ == "__main__":
    predictor = TranslationPredictor()
    print("="*60)
    print("🧪 TRANSLATION TEST")
    print("="*60)
    
    print(f"\n📊 Available Languages: {predictor.get_languages()}")
    
    tests = [
        ("Good morning", "Luganda"),
        ("Thank you very much", "Luganda"),
        ("I love you", "Luganda"),
        ("Good morning my friend", "Luganda"),  # Word-by-word
        ("How are you today", "Luganda"),       # Word-by-word
        ("I love you", "Acholi"),
    ]
    
    print("\n📊 Results:")
    print("-"*60)
    for text, lang in tests:
        result = predictor.translate(text, lang)
        if result.get('success'):
            print(f"✅ '{text}' → {lang}: {result['translation']}")
            print(f"   Model: {result.get('model_used', 'Unknown')}")
            print(f"   Confidence: {result.get('confidence', 'N/A')}")
        else:
            print(f"❌ '{text}' → {lang}: {result.get('error')}")
        print()