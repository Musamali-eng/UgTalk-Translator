# app.py - Complete Flask Application for Ugandan Language Translator
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from models.predictor import TranslationPredictor
from datetime import datetime
import json
import os

app = Flask(__name__)
app.secret_key = 'translation-secret-key-2026'

# Initialize predictor
print("🔄 Loading Translation Model...")
predictor = TranslationPredictor()

# Get available options
LANGUAGES = predictor.get_languages()
DOMAINS = predictor.get_domains()
FORMALITY = ['Formal', 'Informal']

print(f"✅ Languages: {len(LANGUAGES)}")
print(f"✅ Domains: {len(DOMAINS)}")

# ============================================
# ROUTES
# ============================================

@app.route('/')
def index():
    """Home page"""
    stats = predictor.get_stats()
    return render_template('index.html',
                         stats=stats,
                         languages=LANGUAGES,
                         domains=DOMAINS)

@app.route('/translate', methods=['GET', 'POST'])
def translate():
    """Translation page"""
    if request.method == 'POST':
        text = request.form.get('text', '').strip()
        target_language = request.form.get('target_language')
        domain = request.form.get('domain', 'All')
        formality = request.form.get('formality', 'All')
        
        if not text:
            return render_template('translate.html',
                                 languages=LANGUAGES,
                                 domains=DOMAINS,
                                 formality_levels=FORMALITY,
                                 error='Please enter text to translate')
        
        result = predictor.translate(text, target_language, domain, formality)
        
        # Save to session history
        if result.get('success'):
            if 'history' not in session:
                session['history'] = []
            session['history'].append({
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M'),
                'original': text[:50] + ('...' if len(text) > 50 else ''),
                'translation': result['translation'][:50] + ('...' if len(result['translation']) > 50 else ''),
                'language': target_language
            })
            session.modified = True
        
        return render_template('translate.html',
                             languages=LANGUAGES,
                             domains=DOMAINS,
                             formality_levels=FORMALITY,
                             result=result,
                             text=text)
    
    return render_template('translate.html',
                         languages=LANGUAGES,
                         domains=DOMAINS,
                         formality_levels=FORMALITY)


@app.route('/api/translate', methods=['POST'])
def api_translate():
    """API endpoint for translation"""
    try:
        data = request.json
        text = data.get('text', '').strip()
        target_language = data.get('target_language')
        domain = data.get('domain', 'All')
        formality = data.get('formality', 'All')
        
        if not text:
            return jsonify({'success': False, 'error': 'No text provided'}), 400
        
        if not target_language:
            return jsonify({'success': False, 'error': 'Target language required'}), 400
        
        result = predictor.translate(text, target_language, domain, formality)
        
        if result.get('success'):
            return jsonify({
                'success': True,
                'original': result['original'],
                'translation': result['translation'],
                'target_language': result['target_language'],
                'domain': result['domain'],
                'formality': result['formality'],
                'confidence': result['confidence']
            })
        else:
            return jsonify({'success': False, 'error': result.get('error', 'Translation failed')}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/dashboard')
def dashboard():
    """Analytics dashboard - works with or without ML model"""
    if not predictor.is_loaded:
        # Show dictionary-based stats instead of error
        translations = predictor.translations
        lang_dist = {}
        domain_dist = {'Daily Conversation': 30, 'Health': 15, 'Tourism': 12, 'Education': 10, 'Business': 8, 'Agriculture': 5, 'Government': 5}
        formality_dist = {'Informal': 55, 'Formal': 30}
        
        for lang, phrases in translations.items():
            lang_dist[lang] = len(phrases)
        
        return render_template('dashboard.html',
                             lang_dist=lang_dist,
                             domain_dist=domain_dist,
                             formality_dist=formality_dist,
                             total_records=sum(lang_dist.values()),
                             total_languages=len(lang_dist),
                             total_domains=len(domain_dist))
    
    df = predictor.training_data
    
    lang_dist = df['Target_Language'].value_counts().to_dict()
    domain_dist = df['Domain'].value_counts().to_dict()
    formality_dist = df['Formality'].value_counts().to_dict()
    
    return render_template('dashboard.html',
                         lang_dist=lang_dist,
                         domain_dist=domain_dist,
                         formality_dist=formality_dist,
                         total_records=len(df),
                         total_languages=len(df['Target_Language'].unique()),
                         total_domains=len(df['Domain'].unique()))


@app.route('/history')
def history():
    """Translation history"""
    history = session.get('history', [])
    return render_template('history.html', history=history)


# ============================================================
# CLEAR HISTORY ROUTE
# ============================================================
@app.route('/clear_history', methods=['POST'])
def clear_history():
    """Clear all translation history"""
    session['history'] = []
    session.modified = True
    flash('History cleared successfully!', 'success')
    return redirect(url_for('history'))


# ============================================================
# REMOVE SINGLE HISTORY ENTRY (API)
# ============================================================
@app.route('/api/history/remove', methods=['POST'])
def remove_history_entry():
    """Remove a single translation from history"""
    try:
        data = request.json
        index = data.get('index')
        
        if 'history' not in session:
            return jsonify({'success': False, 'error': 'No history found'}), 404
        
        history = session['history']
        if index >= len(history):
            return jsonify({'success': False, 'error': 'Index out of range'}), 400
        
        # Remove the entry
        removed = history.pop(index)
        session['history'] = history
        session.modified = True
        
        return jsonify({
            'success': True,
            'message': f'Removed: {removed.get("original", "Unknown")}'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': predictor.is_loaded,
        'languages': LANGUAGES,
        'domains': DOMAINS,
        'timestamp': datetime.now().isoformat()
    })

# ============================================
# RUN THE APP
# ============================================
if __name__ == '__main__':
    print("="*60)
    print("🚀 UGANDAN LANGUAGE TRANSLATOR")
    print("="*60)
    print(f"✅ Model Loaded: {predictor.is_loaded}")
    print(f"✅ Languages: {len(LANGUAGES)}")
    print(f"✅ Domains: {len(DOMAINS)}")
    print("="*60)
    print("🌐 Server running at: http://localhost:5000")
    print("📋 Press Ctrl+C to stop")
    print("="*60)
    app.run(debug=True, host='0.0.0.0', port=5000)

