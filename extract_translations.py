# extract_translations.py
import pandas as pd
import re
import json

def extract_translation(text):
    """Extract actual translation from dataset format"""
    if isinstance(text, str):
        if '[' in text and ']' in text:
            parts = text.split(']')
            if len(parts) > 1:
                return parts[1].strip()
        match = re.search(r'\]\s*(.+)$', text)
        if match:
            return match.group(1).strip()
        return text
    return text

# Load dataset
df = pd.read_csv('data/Language_translation_models_dataset.csv')

# Extract clean translations
df['Target_Text_Cleaned'] = df['Target_Text'].apply(extract_translation)
df['Source_Text_Cleaned'] = df['Source_Text'].apply(lambda x: x.strip() if isinstance(x, str) else x)

# Create translation dictionary
translations = {}

for lang in df['Target_Language'].unique():
    lang_df = df[df['Target_Language'] == lang]
    translations[lang] = {}
    
    for _, row in lang_df.iterrows():
        source = row['Source_Text_Cleaned'].lower().strip()
        target = row['Target_Text_Cleaned']
        if source and target:
            translations[lang][source] = target

# Print sample translations for each language
print("=" * 70)
print("📊 TRANSLATIONS FROM DATASET")
print("=" * 70)

for lang, trans in translations.items():
    print(f"\n🔷 {lang}:")
    for source, target in list(trans.items())[:5]:
        print(f"   {source} → {target}")

# Save to JSON
with open('models/translations.json', 'w') as f:
    json.dump(translations, f, indent=2, ensure_ascii=False)

print("\n✅ Translations saved to models/translations.json")