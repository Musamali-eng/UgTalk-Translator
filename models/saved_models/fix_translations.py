# fix_translations.py
import pandas as pd
import re

def extract_translation(text):
    """Extract actual translation from dataset format"""
    if isinstance(text, str):
        # Check if it has the placeholder format
        if '[' in text and ']' in text:
            # Extract everything after the closing bracket
            parts = text.split(']')
            if len(parts) > 1:
                translation = parts[1].strip()
                if translation:
                    return translation
        # Also handle cases like "[Luganda translation] Webale nnyo"
        match = re.search(r'\]\s*(.+)$', text)
        if match:
            return match.group(1).strip()
        return text
    return text

# Load the dataset
df = pd.read_csv('data/Language_translation_models_dataset.csv')

# Fix Target_Text
df['Target_Text_Fixed'] = df['Target_Text'].apply(extract_translation)

# Check results
print("📊 Sample translations before and after fixing:")
print("="*60)
for i in range(10):
    print(f"Before: {df['Target_Text'].iloc[i]}")
    print(f"After:  {df['Target_Text_Fixed'].iloc[i]}")
    print()

# Save fixed dataset
df.to_csv('data/Language_translation_models_dataset_fixed.csv', index=False)
print("✅ Fixed dataset saved as: data/Language_translation_models_dataset_fixed.csv")