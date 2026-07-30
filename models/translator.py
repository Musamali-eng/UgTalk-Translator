"""
VisionLens AI - UgTalk Translation Engine
Bi-directional English to Ugandan Language Translation
Supports: Luganda, Lusoga, Acholi, Runyankole, Ateso, Lugbara, Rukiga
"""

import re
import os

try:
    import joblib
    HAS_JOBLIB = True
except ImportError:
    HAS_JOBLIB = False


class TranslationPredictor:
    """
    Translation engine that works with or without pre-trained ML models.
    Falls back gracefully to a comprehensive dictionary-based system.
    """

    def __init__(self):
        self.vectorizer = None
        self.language_models = None
        self.le_language = None
        self.le_domain = None
        self.le_formality = None
        self.training_data = None
        self.is_loaded = False
        self.load_models()
        self._build_dictionaries()

    # ------------------------------------------------------------------
    # DICTIONARY DATA
    # ------------------------------------------------------------------

    def _build_dictionaries(self):
        """Build forward + reverse lookup dictionaries for all 7 languages."""
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

        # Forward: (english_phrase_lower, language) -> ugandan_translation
        self.exact_matches = {}
        # Reverse: ugandan_phrase_lower -> (english_phrase, language)
        self.reverse_matches = {}

        for lang, phrases in self.translations.items():
            for phrase, translation in phrases.items():
                key = (phrase.lower().strip(), lang)
                self.exact_matches[key] = translation
                ug_lower = translation.lower().strip()
                self.reverse_matches[ug_lower] = (phrase, lang)

    # ------------------------------------------------------------------
    # MODEL LOADING
    # ------------------------------------------------------------------

    def load_models(self):
        """Try loading pre-trained ML models; fall back to dictionary."""
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            model_dir = os.path.join(base_dir, 'models', 'saved_models')

            required = [
                'vectorizer.pkl', 'language_models.pkl', 'le_language.pkl',
                'le_domain.pkl', 'le_formality.pkl', 'training_data.pkl'
            ]
            missing = [f for f in required if not os.path.exists(os.path.join(model_dir, f))]

            if missing or not HAS_JOBLIB:
                print(f"Translation: using dictionary mode ({len(missing)} model files missing)")
                self.is_loaded = False
                return False

            self.vectorizer = joblib.load(os.path.join(model_dir, 'vectorizer.pkl'))
            self.language_models = joblib.load(os.path.join(model_dir, 'language_models.pkl'))
            self.le_language = joblib.load(os.path.join(model_dir, 'le_language.pkl'))
            self.le_domain = joblib.load(os.path.join(model_dir, 'le_domain.pkl'))
            self.le_formality = joblib.load(os.path.join(model_dir, 'le_formality.pkl'))
            self.training_data = joblib.load(os.path.join(model_dir, 'training_data.pkl'))
            self.is_loaded = True
            print(f"Translation predictor loaded ({len(self.le_language.classes_)} languages)")
            return True
        except Exception as e:
            print(f"Translation: dictionary mode ({e})")
            self.is_loaded = False
            return False

    # ------------------------------------------------------------------
    # PUBLIC HELPERS
    # ------------------------------------------------------------------

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
                'status': 'dictionary',
                'languages': len(self.get_languages()),
                'domains': 7,
                'total_samples': 0
            }
        return {
            'status': 'ml_model',
            'languages': len(self.get_languages()),
            'domains': len(self.get_domains()),
            'total_samples': len(self.training_data) if self.training_data is not None else 0
        }

    # ------------------------------------------------------------------
    # TEXT CLEANING
    # ------------------------------------------------------------------

    def clean_text(self, text):
        if not isinstance(text, str):
            text = str(text)
        text = ' '.join(text.split())
        text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
        return text.strip()

    # ------------------------------------------------------------------
    # MATCHING LOGIC
    # ------------------------------------------------------------------

    def find_best_match(self, text, target_language):
        """Forward: English to Ugandan"""
        text_lower = text.lower().strip()
        key = (text_lower, target_language)
        if key in self.exact_matches:
            return self.exact_matches[key]

        lang_phrases = self.translations.get(target_language, {})
        best, best_score = None, 0
        for phrase, translation in lang_phrases.items():
            if phrase in text_lower or text_lower in phrase:
                score = len(phrase) / max(len(text_lower), 1)
                if score > best_score:
                    best_score = score
                    best = translation
        return best

    def find_reverse_match(self, text):
        """Reverse: Ugandan to English"""
        text_lower = text.lower().strip()
        if text_lower in self.reverse_matches:
            return self.reverse_matches[text_lower]

        best, best_score = None, 0
        for ug_phrase, (en_phrase, lang) in self.reverse_matches.items():
            if ug_phrase in text_lower or text_lower in ug_phrase:
                score = len(ug_phrase) / max(len(text_lower), 1)
                if score > best_score:
                    best_score = score
                    best = (en_phrase, lang)
        return best

    # ------------------------------------------------------------------
    # SENTENCE / WORD-LEVEL TRANSLATION
    # ------------------------------------------------------------------

    def _translate_sentence(self, text, target_language):
        """
        Translate a full sentence by doing word-by-word and phrase matching.
        Unknown words are kept as-is in the output.
        """
        text_lower = text.lower().strip()
        lang_phrases = self.translations.get(target_language, {})

        result_text = text_lower
        matched_any = False

        # First pass: match multi-word phrases (longest first)
        sorted_phrases = sorted(lang_phrases.keys(), key=lambda p: -len(p))
        for phrase in sorted_phrases:
            if len(phrase.split()) > 1:  # multi-word phrases only
                if phrase in result_text:
                    translation = lang_phrases[phrase]
                    result_text = result_text.replace(phrase, f"[[[{translation}]]]", 1)
                    matched_any = True

        # Second pass: match individual words
        for word in list(result_text.split()):
            # Strip punctuation for matching
            clean_word = word.strip(".,!?;:'\"[]{}()").lower()
            # Skip if already a placeholder
            if clean_word.startswith('[[[') and clean_word.endswith(']]]'):
                continue
            if clean_word in lang_phrases:
                translation = lang_phrases[clean_word]
                result_text = re.sub(r'\b' + re.escape(clean_word) + r'\b', f"[[[{translation}]]]", result_text)
                matched_any = True

        # Replace placeholders with actual translations
        result_text = re.sub(r'\[\[\[(.*?)\]\]\]', r'\1', result_text)

        # Capitalize first letter
        if result_text:
            result_text = result_text[0].upper() + result_text[1:]

        return result_text if matched_any else None

    # ------------------------------------------------------------------
    # MAIN TRANSLATE METHOD
    # ------------------------------------------------------------------

    def translate(self, text, target_language, domain=None, formality=None):
        """Bi-directional translate: English to Ugandan"""
        if target_language not in self.get_languages():
            return {
                'success': False,
                'error': 'Language "{}" not supported. Available: {}'.format(
                    target_language, ", ".join(self.get_languages()))
            }

        text = text.strip()
        if not text:
            return {'success': False, 'error': 'Please enter text to translate'}

        cleaned = self.clean_text(text)

        # 1) Forward match - exact phrase match
        result = self.find_best_match(cleaned, target_language)
        if result:
            return {
                'success': True,
                'original': text,
                'translation': result,
                'target_language': target_language,
                'domain': 'Dictionary',
                'formality': 'Informal',
                'confidence': 1.0,
                'direction': 'forward'
            }

        # 2) Sentence-level translation (word-by-word + phrase matching)
        sentence_result = self._translate_sentence(cleaned, target_language)
        if sentence_result:
            original_words = set(cleaned.lower().split())
            lang_phrases = self.translations.get(target_language, {})
            translated_count = sum(1 for w in original_words if w in lang_phrases)
            total_words = len(original_words)
            confidence = round(min(1.0, translated_count / max(total_words, 1)), 2)

            return {
                'success': True,
                'original': text,
                'translation': sentence_result,
                'target_language': target_language,
                'domain': 'Dictionary',
                'formality': 'Informal',
                'confidence': max(confidence, 0.5),
                'direction': 'sentence'
            }

        # 3) Reverse match (Ugandan phrase to English explanation)
        rev = self.find_reverse_match(cleaned)
        if rev:
            en_phrase, detected_lang = rev
            return {
                'success': True,
                'original': text,
                'translation': en_phrase,
                'target_language': target_language,
                'detected_source_language': detected_lang,
                'domain': 'Dictionary',
                'formality': 'Informal',
                'confidence': 1.0,
                'direction': 'reverse'
            }

        # 4) ML model fallback
        if self.is_loaded and target_language in self.language_models:
            try:
                vec = self.vectorizer.transform([cleaned])
                lm = self.language_models[target_language]
                distances, indices = lm['model'].kneighbors(vec)
                if indices[0].size and indices[0][0] < len(lm['texts']):
                    t = lm['texts'][indices[0][0]]
                    t = self._extract_translation(t)
                    return {
                        'success': True,
                        'original': text,
                        'translation': t,
                        'target_language': target_language,
                        'domain': lm['domains'][indices[0][0]],
                        'formality': lm['formality'][indices[0][0]],
                        'confidence': round(max(0, 1 - distances[0][0]), 3),
                        'direction': 'ml_model'
                    }
            except Exception:
                pass

        # 5) Helpful error with suggestions
        suggestions = []
        for lang_name, phrases in self.translations.items():
            for en_phrase in phrases:
                if any(word in cleaned.lower() for word in en_phrase.lower().split()):
                    suggestions.append("'{}'".format(en_phrase))
                    if len(suggestions) >= 3:
                        break
            if len(suggestions) >= 3:
                break

        msg = 'Could not translate "{}" to {}.'.format(text, target_language)
        if suggestions:
            msg += ' Try: {}'.format(", ".join(suggestions))
        else:
            msg += ' Try a shorter/common phrase.'
        return {'success': False, 'error': msg}

    @staticmethod
    def _extract_translation(text):
        if isinstance(text, str) and '[' in text and ']' in text:
            parts = text.split(']')
            if len(parts) > 1 and parts[1].strip():
                return parts[1].strip()
        return text

