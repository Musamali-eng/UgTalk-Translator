# models/predictor.py - FIXED (No external libraries)
import pandas as pd
import numpy as np
import joblib
import re
import os

class TranslationPredictor:
    def __init__(self):
        self.vectorizer = None
        self.language_models = None
        self.le_language = None
        self.le_domain = None
        self.le_formality = None
        self.training_data = None
        self.is_loaded = False
        self.load_models()
        self._create_translation_dictionary()
    
    def _create_translation_dictionary(self):
        """Create comprehensive translation dictionary for all languages (bi-directional)"""
        self.translations = {
            'Luganda': {
                'thank you': 'Webale nnyo',
                'thanks': 'Webale',
                'good morning': 'Wasuze otya',
                'good afternoon': 'Osiibye otya',
                'good evening': 'Osiibye otya',
                'welcome': 'Tukusanyukidde',
                'hello': 'Ki kati',
                'hi': 'Ki kati',
                'goodbye': 'Weeraba',
                'bye': 'Weeraba',
                'open the door': 'Ggulawo oluggi',
                'close the door': 'Ggalawo oluggi',
                'how are you': 'Oli otya',
                'i am fine': 'Ndi bulungi',
                'i am okay': 'Ndi bulungi',
                'what is your name': 'Erinnya lyo ani',
                'my name is': 'Erinnya lyange',
                'yes': 'Yee',
                'no': 'Nedda',
                'please': 'Mwebale',
                'sorry': 'Nsonyiwa',
                'help': 'Nnyamba',
                'i need help': 'Nneetaaga obuyambi',
                'where is': 'Kiri wa',
                'how much': 'Sente mmeka',
                'i love you': 'Nkwagala',
                'good': 'Bulungi',
                'bad': 'Bibi',
                'today': 'Leero',
                'tomorrow': 'Nkya',
                'yesterday': 'Jjo',
                'water': 'Amazzi',
                'food': 'Emmere',
                'hospital': 'Eddwaliro',
                'police': 'Pulisi',
                'thank you very much': 'Webale nnyo',
            },
            'Rukiga': {
                'thank you': 'Webale',
                'good morning': 'Oraare gye',
                'good afternoon': 'Osiibye gye',
                'welcome': 'Tusiime',
                'hello': 'Agandi',
                'goodbye': 'Nimwe',
                'open the door': 'Gura omuryango',
                'how are you': 'Oraare gye',
                'i am fine': 'Ndi mwe',
                'what is your name': 'Ishwa ryawe niiwe',
                'my name is': 'Ishwa ryange nii',
                'yes': 'Nee',
                'no': 'Ngangi',
                'please': 'Mwebale',
                'sorry': 'Nsonsiwe',
                'help': 'Nyanba',
                'i love you': 'Ninkukunda',
            },
            'Acholi': {
                'thank you': 'Apwoyo matek',
                'thanks': 'Apwoyo',
                'good morning': 'Itye nino',
                'good afternoon': 'Itye nino',
                'welcome': 'Yin kare',
                'hello': 'Yin kare',
                'goodbye': 'Obedo maber',
                'bye': 'Obedo maber',
                'open the door': 'Yab dog',
                'how are you': 'Itye nino',
                'i am fine': 'Atye maber',
                'what is your name': 'Nyingi ngweni',
                'my name is': 'Nyinga ngwen',
                'yes': 'Ee',
                'no': 'Pe',
                'please': 'Apwoyo',
                'sorry': 'Tim kica',
                'help': 'Konya',
                'i love you': 'Amaro ni',
            },
            'Lusoga': {
                'thank you': 'Webale',
                'good morning': 'Mirembe',
                'good afternoon': 'Osiibye otya',
                'welcome': 'Tukusanyukidde',
                'hello': 'Kale',
                'goodbye': 'Weeraba',
                'bye': 'Weeraba',
                'open the door': 'Ggulawo oluggi',
                'how are you': 'Oli otya',
                'i am fine': 'Ndi bulungi',
                'what is your name': 'Erinnya lyo ani',
                'my name is': 'Erinnya lyange',
                'yes': 'Yee',
                'no': 'Nedda',
                'please': 'Mwebale',
                'sorry': 'Nsonyiwa',
                'help': 'Nnyamba',
                'i love you': 'Nkwagala',
            },
            'Runyankole': {
                'thank you': 'Webale',
                'good morning': 'Oraare gye',
                'good afternoon': 'Osiibye gye',
                'welcome': 'Tusiime',
                'hello': 'Agandi',
                'goodbye': 'Nimwe',
                'bye': 'Nimwe',
                'open the door': 'Gura omuryango',
                'how are you': 'Oraare gye',
                'i am fine': 'Ndi mwe',
                'what is your name': 'Ishwa ryawe niiwe',
                'my name is': 'Ishwa ryange nii',
                'yes': 'Nee',
                'no': 'Ngangi',
                'please': 'Mwebale',
                'sorry': 'Nsonsiwe',
                'help': 'Nyanba',
                'i love you': 'Ninkukunda',
            },
            'Ateso': {
                'thank you': 'Eyalama',
                'good morning': 'Itokei',
                'good afternoon': 'Aitokei',
                'welcome': 'Kale',
                'hello': 'Ayo',
                'goodbye': 'Nayai',
                'bye': 'Nayai',
                'open the door': 'Lok doi',
                'how are you': 'Itokei',
                'i am fine': 'Ito nai',
                'what is your name': 'Eong nike',
                'my name is': 'Eong nia',
                'yes': 'Ee',
                'no': 'Mam',
                'please': 'Eyalama',
                'sorry': 'Naya',
                'help': 'Konya',
                'i love you': 'Eong amaritai',
            },
            'Lugbara': {
                'thank you': 'Mvolo',
                'good morning': 'Molo',
                'good afternoon': 'Molo',
                'welcome': 'Wuruke',
                'hello': 'Molo',
                'goodbye': 'Oru',
                'bye': 'Oru',
                'open the door': 'Ru yi',
                'how are you': 'Molo',
                'i am fine': 'Molo nza',
                'what is your name': 'Ingo ni',
                'my name is': 'Ingo na',
                'yes': 'Ee',
                'no': 'Awa',
                'please': 'Mvolo',
                'sorry': 'Mvolo',
                'help': 'Konya',
                'i love you': 'Ma ti',
            }
        }
        
        # Build forward matches (English phrase → Ugandan)
        self.exact_matches = {}
        # Build reverse matches (Ugandan phrase → English)
        self.reverse_matches = {}  # Maps Ugandan phrase.lower() -> (english_phrase, language)
        
        for lang, phrases in self.translations.items():
            for phrase, translation in phrases.items():
                # Forward: English phrase → Ugandan
                self.exact_matches[(phrase.lower().strip(), lang)] = translation
                # Reverse: Ugandan phrase → English
                ugandan_phrase_lower = translation.lower().strip()
                self.reverse_matches[ugandan_phrase_lower] = (phrase, lang)
    
    def extract_translation(self, text):
        """Extract actual translation from dataset format"""
        if isinstance(text, str):
            if '[' in text and ']' in text:
                parts = text.split(']')
                if len(parts) > 1:
                    translation = parts[1].strip()
                    if translation:
                        return translation
            match = re.search(r'\]\s*(.+)$', text)
            if match:
                return match.group(1).strip()
            return text
        return text
    
    def load_models(self):
        """Load trained models and components"""
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            model_dir = os.path.join(base_dir, 'models', 'saved_models')
            
            required_files = ['vectorizer.pkl', 'language_models.pkl', 'le_language.pkl', 
                            'le_domain.pkl', 'le_formality.pkl', 'training_data.pkl']
            
            missing_files = []
            for file in required_files:
                if not os.path.exists(os.path.join(model_dir, file)):
                    missing_files.append(file)
            
            if missing_files:
                print(f"⚠️ Missing model files: {missing_files}")
                print("⚠️ Using dictionary-based translations only")
                self.is_loaded = False
                return False
            
            self.vectorizer = joblib.load(os.path.join(model_dir, 'vectorizer.pkl'))
            self.language_models = joblib.load(os.path.join(model_dir, 'language_models.pkl'))
            self.le_language = joblib.load(os.path.join(model_dir, 'le_language.pkl'))
            self.le_domain = joblib.load(os.path.join(model_dir, 'le_domain.pkl'))
            self.le_formality = joblib.load(os.path.join(model_dir, 'le_formality.pkl'))
            self.training_data = joblib.load(os.path.join(model_dir, 'training_data.pkl'))
            self.is_loaded = True
            print("✅ Translation Predictor loaded successfully!")
            print(f"   Languages: {len(self.le_language.classes_)}")
            print(f"   Domains: {len(self.le_domain.classes_)}")
            return True
        except Exception as e:
            print(f"⚠️ Error loading models: {e}")
            print("⚠️ Using dictionary-based translations only")
            self.is_loaded = False
            return False
    
    def get_languages(self):
        if self.is_loaded and self.le_language is not None:
            return self.le_language.classes_.tolist()
        return list(self.translations.keys())
    
    def get_domains(self):
        if self.is_loaded and self.le_domain is not None:
            return self.le_domain.classes_.tolist()
        return ['Daily Conversation', 'Health', 'Tourism', 'Education', 'Business', 'Agriculture', 'Government']
    
    def get_formality_levels(self):
        return ['Formal', 'Informal']
    
    def get_stats(self):
        if not self.is_loaded:
            return {
                'status': 'dictionary_only',
                'languages': len(self.get_languages()),
                'domains': 7,
                'formality_levels': 2,
                'total_samples': 0
            }
        
        return {
            'status': 'loaded',
            'languages': len(self.get_languages()),
            'domains': len(self.get_domains()),
            'formality_levels': len(self.get_formality_levels()),
            'total_samples': len(self.training_data) if self.training_data is not None else 0
        }
    
    def clean_text(self, text):
        if not isinstance(text, str):
            text = str(text)
        text = ' '.join(text.split())
        text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
        return text.strip()
    
    def find_best_match(self, text, target_language):
        """Find the best translation match (forward: English → Ugandan)"""
        text_lower = text.lower().strip()
        
        # Check exact match
        if (text_lower, target_language) in self.exact_matches:
            return self.exact_matches[(text_lower, target_language)]
        
        # Check partial match
        lang_phrases = self.translations.get(target_language, {})
        best_match = None
        best_score = 0
        
        for phrase, translation in lang_phrases.items():
            # Check if phrase is in text or text is in phrase
            if phrase in text_lower or text_lower in phrase:
                score = len(phrase) / max(len(text_lower), 1)
                if score > best_score:
                    best_score = score
                    best_match = translation
        
        return best_match
    
    def find_reverse_match(self, text):
        """Find reverse match (Ugandan → English). Returns (english_phrase, source_language) or None"""
        text_lower = text.lower().strip()
        
        # Check exact reverse match
        if text_lower in self.reverse_matches:
            return self.reverse_matches[text_lower]
        
        # Check partial reverse match
        best_match = None
        best_score = 0
        
        for ug_phrase, (en_phrase, lang) in self.reverse_matches.items():
            if ug_phrase in text_lower or text_lower in ug_phrase:
                score = len(ug_phrase) / max(len(text_lower), 1)
                if score > best_score:
                    best_score = score
                    best_match = (en_phrase, lang)
        
        return best_match
    
    def detect_language(self, text):
        """Detect if text is likely a Ugandan phrase or English"""
        text_lower = text.lower().strip()
        
        # Ugandan phrases typically have certain characteristics
        # Check if text matches any known Ugandan phrase
        for ug_phrase in self.reverse_matches:
            if ug_phrase in text_lower or text_lower in ug_phrase:
                return 'ugandan'
        
        # Check if text matches any known English phrase
        for lang, phrases in self.translations.items():
            for en_phrase in phrases:
                if en_phrase.lower() in text_lower or text_lower in en_phrase.lower():
                    return 'english'
        
        return 'unknown'
    
    def translate(self, text, target_language, domain=None, formality=None):
        """Translate text between English and Ugandan languages (bi-directional)"""
        if target_language not in self.get_languages():
            return {
                'success': False, 
                'error': f'Language "{target_language}" not supported. Available: {self.get_languages()}'
            }
        
        text = text.strip()
        if not text:
            return {'success': False, 'error': 'Please enter text to translate'}
        
        clean_text = self.clean_text(text)
        
        # STEP 1: Try forward match (English → Ugandan)
        translation = self.find_best_match(clean_text, target_language)
        if translation:
            return {
                'success': True,
                'original': text,
                'translation': translation,
                'target_language': target_language,
                'domain': 'Dictionary',
                'formality': 'Informal',
                'confidence': 1.0,
                'similar_text': text
            }
        
        # STEP 2: Try reverse match (Ugandan phrase → English explanation)
        # This handles case where user types a Luganda phrase and selects Luganda (meaning they want English)
        reverse_result = self.find_reverse_match(clean_text)
        if reverse_result:
            en_phrase, detected_lang = reverse_result
            return {
                'success': True,
                'original': text,
                'translation': en_phrase,
                'target_language': target_language,
                'detected_source_language': detected_lang,
                'domain': 'Dictionary',
                'formality': 'Informal',
                'confidence': 1.0,
                'similar_text': text
            }
        
        # STEP 3: Try model-based translation (if available)
        if self.is_loaded and target_language in self.language_models:
            try:
                text_vector = self.vectorizer.transform([clean_text])
                lang_model = self.language_models[target_language]
                distances, indices = lang_model['model'].kneighbors(text_vector)
                
                matches = []
                for idx in indices[0]:
                    if idx < len(lang_model['texts']):
                        translation_text = lang_model['texts'][idx]
                        # Clean translation if it has placeholder
                        translation_text = self.extract_translation(translation_text)
                        matches.append({
                            'translation': translation_text,
                            'domain': lang_model['domains'][idx],
                            'formality': lang_model['formality'][idx],
                            'distance': float(distances[0][list(indices[0]).index(idx)])
                        })
                
                if matches:
                    best = matches[0]
                    return {
                        'success': True,
                        'original': text,
                        'translation': best['translation'],
                        'target_language': target_language,
                        'domain': best['domain'],
                        'formality': best['formality'],
                        'confidence': round(max(0, 1 - best['distance']), 3),
                        'similar_text': text
                    }
            except Exception as e:
                pass
        
        # STEP 4: Return helpful error with suggestions
        suggestions = []
        for lang, phrases in self.translations.items():
            for en_phrase in phrases:
                if any(word in clean_text.lower() for word in en_phrase.lower().split()):
                    suggestions.append(f"'{en_phrase}' → {lang}")
                    if len(suggestions) >= 3:
                        break
            if len(suggestions) >= 3:
                break
        
        error_msg = f'Could not translate "{text}" to {target_language}.'
        if suggestions:
            error_msg += f' Did you mean one of these? {", ".join(suggestions)}'
        else:
            error_msg += ' Please try a different phrase.'
        
        return {
            'success': False,
            'error': error_msg
        }

# Test function
if __name__ == "__main__":
    predictor = TranslationPredictor()
    print("\n🧪 Testing translations:")
    test_cases = [
        ("Thank you", "Luganda"),
        ("Webale nnyo", "Luganda"),  # Reverse: Luganda → English
        ("Good morning", "Rukiga"),
        ("Good morning", "Acholi"),
        ("Welcome", "Luganda"),
        ("Oli otya", "Luganda"),  # Reverse: Luganda → English
        ("Open the door", "Ateso"),
        ("Nkwagala", "Luganda"),  # Reverse: Luganda → English
        ("What is your name", "Luganda"),
        ("Goodbye", "Runyankole"),
    ]
    
    for text, lang in test_cases:
        result = predictor.translate(text, lang)
        if result.get('success'):
            direction = "REVERSE" if result.get('detected_source_language') else "FORWARD"
            print(f"\n✅ [{direction}] '{text}' → {lang}: {result['translation']}")
            print(f"   Confidence: {result.get('confidence', 'N/A')}")
        else:
            print(f"\n❌ '{text}' → {lang}: {result.get('error')}")

