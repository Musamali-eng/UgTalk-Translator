# fix_and_retrain.py
import pandas as pd
import re
import joblib
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import LabelEncoder

def extract_translation(text):
    """Extract actual translation from dataset format"""
    if isinstance(text, str):
        if '[' in text and ']' in text:
            parts = text.split(']')
            if len(parts) > 1:
                translation = parts[1].strip()
                if translation:
                    return translation
        import re
        match = re.search(r'\]\s*(.+)$', text)
        if match:
            return match.group(1).strip()
        return text
    return text

print("="*60)
print("🔄 RETRAINING WITH FIXED TRANSLATIONS")
print("="*60)

# Load dataset
df = pd.read_csv('data/Language_translation_models_dataset.csv')
print(f"📊 Loaded {len(df)} records")

# Fix translations
df['Target_Text_Fixed'] = df['Target_Text'].apply(extract_translation)

# Show sample
print("\n📊 Sample translations BEFORE and AFTER fixing:")
print("="*50)
for i in range(5):
    print(f"BEFORE: {df['Target_Text'].iloc[i]}")
    print(f"AFTER:  {df['Target_Text_Fixed'].iloc[i]}")
    print()

# Clean source text
def clean_text(text):
    if isinstance(text, str):
        text = ' '.join(text.split())
        import re
        text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
        return text
    return text

df['Source_Text_Cleaned'] = df['Source_Text'].apply(clean_text)

# Remove empty rows
df = df[df['Target_Text_Fixed'].notna()]
df = df[df['Target_Text_Fixed'].str.strip() != '']
df = df[df['Source_Text_Cleaned'].notna()]
df = df[df['Source_Text_Cleaned'].str.strip() != '']

print(f"✅ After cleaning: {len(df)} records")

# Encode
le_language = LabelEncoder()
le_domain = LabelEncoder()
le_formality = LabelEncoder()

df['Language_encoded'] = le_language.fit_transform(df['Target_Language'])
df['Domain_encoded'] = le_domain.fit_transform(df['Domain'])
df['Formality_encoded'] = le_formality.fit_transform(df['Formality'])

# Vectorize
vectorizer = TfidfVectorizer(max_features=1000, stop_words='english', ngram_range=(1, 2))
source_vectors = vectorizer.fit_transform(df['Source_Text_Cleaned'])
print(f"✅ Vectorized: {source_vectors.shape[0]} samples, {source_vectors.shape[1]} features")

# Build language models with FIXED translations
language_models = {}
for lang in df['Target_Language'].unique():
    lang_df = df[df['Target_Language'] == lang]
    lang_vectors = vectorizer.transform(lang_df['Source_Text_Cleaned'])
    model = NearestNeighbors(n_neighbors=3, metric='cosine')
    model.fit(lang_vectors)
    
    language_models[lang] = {
        'model': model,
        'texts': lang_df['Target_Text_Fixed'].values,  # ← USING FIXED TRANSLATIONS
        'domains': lang_df['Domain'].values,
        'formality': lang_df['Formality'].values,
        'sources': lang_df['Source_Text'].values
    }
    print(f"   ✅ {lang}: {len(lang_df)} translations")

# Save models
os.makedirs('models/saved_models', exist_ok=True)
joblib.dump(vectorizer, 'models/saved_models/vectorizer.pkl')
joblib.dump(language_models, 'models/saved_models/language_models.pkl')
joblib.dump(le_language, 'models/saved_models/le_language.pkl')
joblib.dump(le_domain, 'models/saved_models/le_domain.pkl')
joblib.dump(le_formality, 'models/saved_models/le_formality.pkl')
joblib.dump(df, 'models/saved_models/training_data.pkl')

print("\n✅ Model retrained with fixed translations!")

# Quick test
print("\n🧪 Testing:")
predictor = TranslationPredictor()
if predictor.is_loaded:
    result = predictor.translate("Thank you", "Luganda")
    if result.get('success'):
        print(f"   ✅ Translation: {result['translation']}")
    else:
        print(f"   ❌ {result.get('error')}")

print("\n🎉 Restart your Flask app and test!")