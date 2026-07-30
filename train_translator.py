"""
UgTalk Translation Engine - Training Script
Converts the hardcoded dictionary into a proper ML training dataset,
trains TF-IDF + kNN models, and saves everything as pickle files.

After running this script, the translator will use ML-based similarity
matching instead of exact dictionary lookups — allowing it to translate
phrases NOT in the original dictionary by finding the closest match.

Usage:
    python train_translator.py
"""

import os
import re
import json
import pickle
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import LabelEncoder

# Ensure joblib is available
try:
    import joblib
except ImportError:
    os.system("pip install joblib scikit-learn")
    import joblib


def build_training_data():
    """
    Convert the hardcoded dictionary translations into a structured
    training dataset with columns:
        - english_text: the English phrase
        - ugandan_text: the Ugandan translation
        - language: which Ugandan language
        - domain: topic category
        - formality: Formal or Informal
    """
    # =================================================================
    # SOURCE DICTIONARY (same as in models/translator.py)
    # =================================================================
    translations = {
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

    # Domain mapping for each phrase (categorizes the context)
    domain_map = {
        'thank you': 'Daily Conversation',
        'thanks': 'Daily Conversation',
        'good morning': 'Daily Conversation',
        'good afternoon': 'Daily Conversation',
        'good evening': 'Daily Conversation',
        'welcome': 'Daily Conversation',
        'hello': 'Daily Conversation',
        'hi': 'Daily Conversation',
        'goodbye': 'Daily Conversation',
        'bye': 'Daily Conversation',
        'open the door': 'Daily Conversation',
        'close the door': 'Daily Conversation',
        'how are you': 'Daily Conversation',
        'i am fine': 'Health',
        'i am okay': 'Health',
        'what is your name': 'Daily Conversation',
        'my name is': 'Daily Conversation',
        'yes': 'Daily Conversation',
        'no': 'Daily Conversation',
        'please': 'Daily Conversation',
        'sorry': 'Daily Conversation',
        'help': 'Health',
        'i need help': 'Health',
        'where is': 'Tourism',
        'how much': 'Business',
        'i love you': 'Daily Conversation',
        'good': 'Daily Conversation',
        'bad': 'Daily Conversation',
        'today': 'Daily Conversation',
        'tomorrow': 'Daily Conversation',
        'yesterday': 'Daily Conversation',
        'water': 'Health',
        'food': 'Health',
        'hospital': 'Health',
        'police': 'Government',
        'thank you very much': 'Daily Conversation',
    }

    # Formality mapping
    formality_map = {
        'thank you': 'Informal',
        'thanks': 'Informal',
        'good morning': 'Formal',
        'good afternoon': 'Formal',
        'good evening': 'Formal',
        'welcome': 'Formal',
        'hello': 'Informal',
        'hi': 'Informal',
        'goodbye': 'Informal',
        'bye': 'Informal',
        'open the door': 'Informal',
        'close the door': 'Informal',
        'how are you': 'Informal',
        'i am fine': 'Informal',
        'i am okay': 'Informal',
        'what is your name': 'Informal',
        'my name is': 'Informal',
        'yes': 'Informal',
        'no': 'Informal',
        'please': 'Formal',
        'sorry': 'Informal',
        'help': 'Informal',
        'i need help': 'Formal',
        'where is': 'Informal',
        'how much': 'Informal',
        'i love you': 'Informal',
        'good': 'Informal',
        'bad': 'Informal',
        'today': 'Informal',
        'tomorrow': 'Informal',
        'yesterday': 'Informal',
        'water': 'Informal',
        'food': 'Informal',
        'hospital': 'Formal',
        'police': 'Formal',
        'thank you very much': 'Formal',
    }

    # Build the structured dataset
    english_texts = []
    ugandan_texts = []
    languages = []
    domains = []
    formality_levels = []

    for lang, phrases in translations.items():
        for en_phrase, ug_phrase in phrases.items():
            english_texts.append(en_phrase)
            ugandan_texts.append(ug_phrase)
            languages.append(lang)
            domains.append(domain_map.get(en_phrase, 'Daily Conversation'))
            formality_levels.append(formality_map.get(en_phrase, 'Informal'))

            # Also add the reverse direction (Ugandan → English) to double the dataset
            # This helps the model learn bidirectional translations
            english_texts.append(ug_phrase)
            ugandan_texts.append(en_phrase)
            languages.append(lang)
            domains.append(domain_map.get(en_phrase, 'Daily Conversation'))
            formality_levels.append(formality_map.get(en_phrase, 'Informal'))

    print(f"✅ Built training dataset with {len(english_texts)} samples across {len(translations)} languages")
    print(f"   Languages: {list(translations.keys())}")

    return english_texts, ugandan_texts, languages, domains, formality_levels


def clean_text(text):
    """Basic text cleaning"""
    if not isinstance(text, str):
        text = str(text)
    text = ' '.join(text.split())
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    return text.strip().lower()


def train(english_texts, ugandan_texts, languages, domains, formality_levels):
    """
    Train ML models for the translator:
    1. TF-IDF vectorizer trained on all text (English + Ugandan)
    2. LabelEncoders for language, domain, formality
    3. Per-language kNN models that find closest translation matches
    """
    # Clean all texts
    cleaned_texts = [clean_text(t) for t in english_texts]

    # 1. Train TF-IDF vectorizer on all text
    print("\n🔄 Training TF-IDF vectorizer...")
    vectorizer = TfidfVectorizer(
        max_features=2000,
        analyzer='char_wb',  # character n-grams to handle both English & Ugandan
        ngram_range=(2, 5),
        lowercase=True,
        strip_accents='unicode'
    )
    X = vectorizer.fit_transform(cleaned_texts)
    print(f"   Vectorizer vocab size: {len(vectorizer.get_feature_names_out())}")
    print(f"   Matrix shape: {X.shape}")

    # 2. Train LabelEncoders
    print("\n🔄 Training label encoders...")
    le_language = LabelEncoder()
    le_language.fit(languages)
    print(f"   Languages: {le_language.classes_}")

    le_domain = LabelEncoder()
    le_domain.fit(domains)
    print(f"   Domains: {le_domain.classes_}")

    le_formality = LabelEncoder()
    le_formality.fit(formality_levels)
    print(f"   Formality levels: {le_formality.classes_}")

    # 3. Train per-language kNN models
    print("\n🔄 Training per-language kNN models...")
    language_models = {}

    unique_languages = set(languages)
    for lang in unique_languages:
        # Get indices for this language
        indices = [i for i, l in enumerate(languages) if l == lang]
        if not indices:
            continue

        X_lang = X[indices]
        texts_lang = [ugandan_texts[i] for i in indices]
        domains_lang = [domains[i] for i in indices]
        formality_lang = [formality_levels[i] for i in indices]

        # Use cosine similarity via kNN
        n_samples = X_lang.shape[0]
        n_neighbors = min(3, n_samples)  # At most 3 neighbors, at least 1

        knn = NearestNeighbors(
            n_neighbors=n_neighbors,
            metric='cosine',
            algorithm='brute'
        )
        knn.fit(X_lang)

        language_models[lang] = {
            'model': knn,
            'texts': texts_lang,
            'domains': domains_lang,
            'formality': formality_lang,
            'indices': indices
        }
        print(f"   ✅ {lang}: {n_samples} samples, {n_neighbors} neighbors")

    # 4. Build training data structure (for info/stats)
    training_data = []
    for i in range(len(english_texts)):
        training_data.append({
            'input': english_texts[i],
            'output': ugandan_texts[i],
            'language': languages[i],
            'domain': domains[i],
            'formality': formality_levels[i]
        })

    return vectorizer, language_models, le_language, le_domain, le_formality, training_data


def save_models(vectorizer, language_models, le_language, le_domain, le_formality, training_data):
    """Save all trained models as pickle files"""
    # Ensure output directory exists
    base_dir = os.path.dirname(os.path.abspath(__file__))
    model_dir = os.path.join(base_dir, 'models', 'saved_models')
    os.makedirs(model_dir, exist_ok=True)

    print(f"\n💾 Saving models to: {model_dir}")

    # Save vectorizer
    joblib.dump(vectorizer, os.path.join(model_dir, 'vectorizer.pkl'))
    print("   ✅ vectorizer.pkl")

    # Save language models
    joblib.dump(language_models, os.path.join(model_dir, 'language_models.pkl'))
    print("   ✅ language_models.pkl")

    # Save label encoders
    joblib.dump(le_language, os.path.join(model_dir, 'le_language.pkl'))
    print("   ✅ le_language.pkl")

    joblib.dump(le_domain, os.path.join(model_dir, 'le_domain.pkl'))
    print("   ✅ le_domain.pkl")

    joblib.dump(le_formality, os.path.join(model_dir, 'le_formality.pkl'))
    print("   ✅ le_formality.pkl")

    # Save training data (as JSON for human readability, and pickle for loading)
    with open(os.path.join(model_dir, 'training_data.json'), 'w', encoding='utf-8') as f:
        json.dump(training_data, f, ensure_ascii=False, indent=2)
    joblib.dump(training_data, os.path.join(model_dir, 'training_data.pkl'))
    print("   ✅ training_data.pkl (+ training_data.json for review)")

    # Also copy to data/models/ for consistency
    alt_dir = os.path.join(base_dir, 'data', 'models')
    os.makedirs(alt_dir, exist_ok=True)
    for fname in ['vectorizer.pkl', 'language_models.pkl', 'le_language.pkl',
                  'le_domain.pkl', 'le_formality.pkl', 'training_data.pkl']:
        src = os.path.join(model_dir, fname)
        dst = os.path.join(alt_dir, fname)
        with open(src, 'rb') as f_in:
            with open(dst, 'wb') as f_out:
                f_out.write(f_in.read())
    print(f"   ✅ Also copied to: {alt_dir}")

    print("\n🎉 Training complete! All model files saved successfully.")
    return model_dir


def test_translation(vectorizer, language_models, le_language, training_data):
    """Test the trained model with sample translations"""
    print("\n🧪 Testing trained model with sample translations...")
    print("=" * 60)

    test_phrases = [
        ("thank you", "Luganda"),
        ("good morning", "Acholi"),
        ("how are you", "Runyankole"),
        ("i love you", "Ateso"),
        ("help", "Lugbara"),
        ("goodbye", "Lusoga"),
        ("hospital", "Luganda"),
        ("water", "Rukiga"),
        # Test with phrases NOT in the original dictionary
        ("many thanks", "Luganda"),
        ("i need water", "Luganda"),
        ("good day", "Acholi"),
    ]

    for text, lang in test_phrases:
        cleaned = clean_text(text)
        vec = vectorizer.transform([cleaned])

        if lang in language_models:
            lm = language_models[lang]
            distances, indices = lm['model'].kneighbors(vec)

            if indices[0].size and indices[0][0] < len(lm['texts']):
                translation = lm['texts'][indices[0][0]]
                confidence = round(max(0, 1 - distances[0][0]), 3)
                domain = lm['domains'][indices[0][0]]
                print(f"\n   🔤 '{text}' → {lang}")
                print(f"      Translation: {translation}")
                print(f"      Confidence:  {confidence}")
                print(f"      Domain:      {domain}")
            else:
                print(f"\n   ❌ '{text}' → {lang}: No match found")
        else:
            print(f"\n   ❌ '{text}' → {lang}: Language model not found")

    print("\n" + "=" * 60)


def main():
    print("=" * 60)
    print("   🏋️  UgTalk Translation Engine - Training Script")
    print("=" * 60)

    # Step 1: Build training data from dictionary
    print("\n📦 Step 1: Building training data from dictionary...")
    english_texts, ugandan_texts, languages, domains, formality_levels = build_training_data()

    # Step 2: Train ML models
    print("\n🧠 Step 2: Training ML models...")
    vectorizer, language_models, le_language, le_domain, le_formality, training_data = train(
        english_texts, ugandan_texts, languages, domains, formality_levels
    )

    # Step 3: Save models
    print("\n💾 Step 3: Saving models...")
    model_dir = save_models(
        vectorizer, language_models, le_language, le_domain, le_formality, training_data
    )

    # Step 4: Test
    print("\n🔬 Step 4: Testing trained models...")
    test_translation(vectorizer, language_models, le_language, training_data)

    print(f"\n✅ All done! Models saved to: {model_dir}")
    print("\n📋 To verify: Restart the Flask app and test the translator.")
    print("   It should now use ML models instead of dictionary-only mode.")


if __name__ == '__main__':
    main()

