<<<<<<< HEAD
# app.py
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from models.predictor import TranslationPredictor
from datetime import datetime
import json

app = Flask(__name__)
app.secret_key = 'translation-secret-key-2026'

# Initialize predictor (loads .pkl models)
print("🔄 Loading ML Translation Model...")
predictor = TranslationPredictor()

# Get available options from ML model
LANGUAGES = predictor.get_languages()
DOMAINS = predictor.get_domains()
FORMALITY = ['Formal', 'Informal']

print(f"✅ Languages: {len(LANGUAGES)}")
print(f"✅ Languages: {LANGUAGES}")
print(f"✅ Domains: {len(DOMAINS)}")

# ============================================
# ROUTES
# ============================================
=======
"""
AI-Powered Web Service - Flask Application
Group C - RECESS Final Project 2026
"""

from flask import Flask, render_template, request, jsonify, send_file, session, redirect, url_for, flash
import os
import sys

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config
from models.ml_predictor import MLPredictor
from models.image_predictor import ImagePredictor
from models.translator import TranslationPredictor

app = Flask(__name__)
app.config.from_object(Config)

# Initialize ML-based AI predictor
predictor = MLPredictor()
image_predictor = ImagePredictor()

# Initialize UgTalk Translator
print(" loading UgTalk translation engine...")
translator = TranslationPredictor()
LANGUAGES = translator.get_languages()
DOMAINS = translator.get_domains()
>>>>>>> team-mate/main

@app.route('/')
def index():
    """Home page"""
<<<<<<< HEAD
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
        
        # Pure ML translation (NO dictionary!)
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
=======
    return render_template('index.html')



@app.route('/models')
def models_page():
    """AI model catalogue page."""
    return render_template('models.html')

@app.route('/guide')
def guide():
    """Short guide explaining the available workflows."""
    return render_template('guide.html')

@app.route('/history')
def history():
    """Client-side prediction history page."""
    return render_template('history.html')

@app.route('/predict', methods=['POST'])
def predict():
    """
    API endpoint for AI prediction
    Accepts JSON input with 'text' or 'data' field
    Returns prediction results
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Get input text or data
        input_text = data.get('text', '')
        input_type = data.get('type', 'text')
        model_name = data.get('model', 'sentiment_analysis')
        
        if not input_text:
            return jsonify({'error': 'No input provided'}), 400
        
        if model_name not in predictor.get_available_models():
            return jsonify({
                'error': f'Unsupported model: {model_name}',
                'available_models': predictor.get_available_models()
            }), 400

        # Make prediction using the selected AI model
        result = predictor.predict(input_text, input_type, model_name)
        
        return jsonify({
            'success': True,
            'result': result
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'VisionLens AI',
        'version': '1.0.0'
    })

@app.route('/analyze-image', methods=['POST'])
def analyze_image():
    """Classify an uploaded image with a pretrained vision model."""
    uploaded_file = request.files.get('image')
    if uploaded_file is None or not uploaded_file.filename:
        return jsonify({'error': 'Please upload an image'}), 400

    content_type = uploaded_file.mimetype or ''
    if not content_type.startswith('image/'):
        return jsonify({'error': 'Only image files are supported'}), 400

    try:
        result = image_predictor.predict(uploaded_file.read())
        return jsonify({'success': True, 'result': result})
    except Exception as error:
        return jsonify({'success': False, 'error': str(error)}), 400

@app.route('/api/models')
def list_models():
    """List available AI models"""
    models = predictor.get_available_models()
    return jsonify({
        'models': models
    })

# ============================================================
# UGTALK TRANSLATOR ROUTES
# ============================================================

@app.route('/translate')
def translate_page():
    """Ugandan Language Translator page"""
    return render_template('translate.html',
                         languages=LANGUAGES,
                         domains=DOMAINS)


@app.route('/api/translate', methods=['POST'])
def api_translate():
    """API endpoint for English ↔ Ugandan translation"""
    try:
        data = request.get_json()
>>>>>>> team-mate/main
        text = data.get('text', '').strip()
        target_language = data.get('target_language')
        domain = data.get('domain', 'All')
        formality = data.get('formality', 'All')
<<<<<<< HEAD
        
        if not text:
            return jsonify({'success': False, 'error': 'No text provided'}), 400
        
        if not target_language:
            return jsonify({'success': False, 'error': 'Target language required'}), 400
        
        result = predictor.translate(text, target_language, domain, formality)
        
=======

        if not text:
            return jsonify({'success': False, 'error': 'No text provided'}), 400
        if not target_language:
            return jsonify({'success': False, 'error': 'Target language required'}), 400

        result = translator.translate(text, target_language, domain, formality)

>>>>>>> team-mate/main
        if result.get('success'):
            return jsonify({
                'success': True,
                'original': result['original'],
                'translation': result['translation'],
                'target_language': result['target_language'],
<<<<<<< HEAD
                'domain': result['domain'],
                'formality': result['formality'],
                'confidence': result['confidence'],
                'model_used': result['model_used']
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

@app.route('/clear_history', methods=['POST'])
def clear_history():
    """Clear all translation history"""
    session['history'] = []
    session.modified = True
    flash('History cleared successfully!', 'success')
    return redirect(url_for('history'))

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
    print(f"✅ Languages: {LANGUAGES}")
    print(f"✅ Domains: {len(DOMAINS)}")
    print("="*60)
    print("🌐 Server running at: http://localhost:5000")
    print("📋 Press Ctrl+C to stop")
    print("="*60)
=======
                'domain': result.get('domain', 'Dictionary'),
                'formality': result.get('formality', 'Informal'),
                'confidence': result.get('confidence', 1.0),
                'direction': result.get('direction', 'forward')
            })
        else:
            return jsonify({'success': False, 'error': result.get('error', 'Translation failed')}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/translation-dashboard')
def translation_dashboard():
    """Translation analytics dashboard"""
    lang_dist = {}
    for lang in LANGUAGES:
        phrases = translator.translations.get(lang, {})
        lang_dist[lang] = len(phrases)

    domain_dist = {
        'Daily Conversation': 30, 'Health': 15, 'Tourism': 12,
        'Education': 10, 'Business': 8, 'Agriculture': 5, 'Government': 5
    }
    formality_dist = {'Informal': 55, 'Formal': 30}

    stats = {
        'languages': len(LANGUAGES),
        'domains': len(DOMAINS),
        'total_samples': sum(lang_dist.values()),
        'status': 'active'
    }

    return render_template('translation_dashboard.html',
                         stats=stats,
                         lang_dist=lang_dist,
                         domain_dist=domain_dist,
                         formality_dist=formality_dist)


@app.route('/translator-about')
def translator_about():
    """About the translator feature"""
    return render_template('translator_about.html',
                         languages=LANGUAGES,
                         domains=DOMAINS,
                         stats=translator.get_stats())


@app.route('/clear-translation-history', methods=['POST'])
def clear_translation_history():
    """Clear translation session history"""
    session['translation_history'] = []
    session.modified = True
    return jsonify({'success': True, 'message': 'Translation history cleared'})


# ============================================================
# ERROR HANDLERS
# ============================================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('data', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    os.makedirs('static/images', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    os.makedirs('docs', exist_ok=True)
    
    print("=" * 60)
    print("AI-Powered Web Service - Starting...")
    print("Group C - RECESS Final Project 2026")
    print("=" * 60)
    print(f"Server running at: http://localhost:5000")
    print(f"Health check: http://localhost:5000/api/health")
    print("=" * 60)
    
>>>>>>> team-mate/main
    app.run(debug=True, host='0.0.0.0', port=5000)

