# train_model.py
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import LabelEncoder
import joblib
import os
import json
from datetime import datetime
import re

print("="*70)
print("🌍 LANGUAGE TRANSLATION MODEL - TRAINING")
print("="*70)

# 1. LOAD DATASET
print("\n📂 Loading dataset...")
df = pd.read_csv('data/Language_translation_models_dataset.csv')
print(f"✅ Loaded {len(df)} records")

# 2. DATA CLEANING
print("\n🧹 Cleaning data...")

# Fix Sentence_ID
df['Sentence_ID'] = df['Sentence_ID'].astype(str)

# Clean Target_Text (remove placeholder text)
def clean_target_text(text):
    if isinstance(text, str):
        if '[' in text and ']' in text:
            parts = text.split(']')
            if len(parts) > 1:
                return parts[1].strip()
        return text
    return text

df['Target_Text'] = df['Target_Text'].apply(clean_target_text)

# Clean Source_Text
def clean_source_text(text):
    if isinstance(text, str):
        # Remove S0001 prefixes
        if text.startswith('S0001') and len(text) > 5:
            return text[5:].strip()
        return text
    return text

df['Source_Text'] = df['Source_Text'].apply(clean_source_text)

# Remove empty rows
df = df[df['Target_Text'].notna()]
df = df[df['Target_Text'].str.strip() != '']
df = df[df['Source_Text'].notna()]
df = df[df['Source_Text'].str.strip() != '']

# Clean Formality
df['Formality'] = df['Formality'].fillna('Informal')
df['Formality'] = df['Formality'].replace('unknown', 'Informal')

# Clean Sentence_Length
df['Sentence_Length'] = pd.to_numeric(df['Sentence_Length'], errors='coerce')
df['Sentence_Length'] = df['Sentence_Length'].fillna(df['Sentence_Length'].median())

print(f"✅ Cleaned: {len(df)} records remaining")

# 3. ENCODE CATEGORICAL VARIABLES
print("\n🔢 Encoding categorical variables...")

le_language = LabelEncoder()
le_domain = LabelEncoder()
le_formality = LabelEncoder()

df['Language_encoded'] = le_language.fit_transform(df['Target_Language'])
df['Domain_encoded'] = le_domain.fit_transform(df['Domain'])
df['Formality_encoded'] = le_formality.fit_transform(df['Formality'])

print(f"   Languages: {len(le_language.classes_)}")
print(f"   Domains: {len(le_domain.classes_)}")
print(f"   Formality: {len(le_formality.classes_)}")

# 4. BUILD TRANSLATION MODEL
print("\n🤖 Building Translation Model...")

vectorizer = TfidfVectorizer(
    max_features=1000,
    stop_words='english',
    ngram_range=(1, 2)
)

source_vectors = vectorizer.fit_transform(df['Source_Text'])

# Build language-specific models
language_models = {}
for lang in df['Target_Language'].unique():
    lang_df = df[df['Target_Language'] == lang]
    lang_vectors = vectorizer.transform(lang_df['Source_Text'])
    
    model = NearestNeighbors(n_neighbors=3, metric='cosine')
    model.fit(lang_vectors)
    
    language_models[lang] = {
        'model': model,
        'texts': lang_df['Target_Text'].values,
        'domains': lang_df['Domain'].values,
        'formality': lang_df['Formality'].values,
        'sources': lang_df['Source_Text'].values
    }
    
    print(f"   ✅ {lang}: {len(lang_df)} translations")

# 5. SAVE MODEL
print("\n💾 Saving model...")
os.makedirs('models/saved_models', exist_ok=True)

joblib.dump(vectorizer, 'models/saved_models/vectorizer.pkl')
joblib.dump(le_language, 'models/saved_models/le_language.pkl')
joblib.dump(le_domain, 'models/saved_models/le_domain.pkl')
joblib.dump(le_formality, 'models/saved_models/le_formality.pkl')
joblib.dump(language_models, 'models/saved_models/language_models.pkl')
joblib.dump(df, 'models/saved_models/training_data.pkl')

print("✅ Model saved to 'models/saved_models/'!")

# 6. GENERATE REPORT
print("\n📝 Generating model report...")

report = {
    'total_samples': len(df),
    'languages': df['Target_Language'].unique().tolist(),
    'domains': df['Domain'].unique().tolist(),
    'formality_levels': df['Formality'].unique().tolist(),
    'language_distribution': df['Target_Language'].value_counts().to_dict(),
    'domain_distribution': df['Domain'].value_counts().to_dict(),
    'training_date': datetime.now().isoformat(),
    'model_type': 'TF-IDF + Nearest Neighbors',
    'features': source_vectors.shape[1]
}

with open('models/saved_models/model_report.json', 'w') as f:
    json.dump(report, f, indent=2)

print("\n" + "="*70)
print("🎉 TRAINING COMPLETE!")
print("="*70)
print(f"\n📊 Summary:")
print(f"   Total samples: {len(df)}")
print(f"   Languages: {len(df['Target_Language'].unique())}")
print(f"   Domains: {len(df['Domain'].unique())}")
print(f"   Features: {source_vectors.shape[1]}")