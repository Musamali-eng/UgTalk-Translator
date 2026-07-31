"""
AI-Powered Web Service - Flask Application
Group C - RECESS Final Project 2026
Combined: UgTalk Translator + VisionLens AI Services
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
import os
import sys
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config
from models.ml_predictor import MLPredictor
from models.image_predictor import ImagePredictor
from models.predictor import TranslationPredictor

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = 'translation-secret-key-2026'

# Load AI models
print("Loading VisionLens AI Models...")
predictor = MLPredictor()
image_predictor = ImagePredictor()

print("Loading UgTalk Translation Engine...")
translator = TranslationPredictor()
LANGUAGES = translator.get_languages()
DOMAINS = translator.get_domains()
FORMALITY = ['Formal', 'Informal']

print(f"Languages: {len(LANGUAGES)}")
print(f"Domains: {len(DOMAINS)}")

# Main routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/models')
def models_page():
    return render_template('models.html')

@app.route('/guide')
def guide():
    return render_template('guide.html')



# Prediction API
@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
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

# Image analysis
@app.route('/analyze-image', methods=['POST'])
def analyze_image():
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

# API endpoints
@app.route('/api/models')
def list_models():
    models = predictor.get_available_models()
    return jsonify({'models': models})

@app.route('/api/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'VisionLens AI',
        'version': '1.0.0'
    })

# Translation routes
@app.route('/translate', methods=['GET', 'POST'])
def translate():
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
        
        result = translator.translate(text, target_language, domain, formality)
        
        if result.get('success'):
            if 'translation_history' not in session:
                session['translation_history'] = []
            session['translation_history'].append({
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
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        target_language = data.get('target_language')
        domain = data.get('domain', 'All')
        formality = data.get('formality', 'All')

        if not text:
            return jsonify({'success': False, 'error': 'No text provided'}), 400
        if not target_language:
            return jsonify({'success': False, 'error': 'Target language required'}), 400

        result = translator.translate(text, target_language, domain, formality)

        if result.get('success'):
            return jsonify({
                'success': True,
                'original': result['original'],
                'translation': result['translation'],
                'target_language': result['target_language'],
                'domain': result.get('domain', 'Dictionary'),
                'formality': result.get('formality', 'Informal'),
                'confidence': result.get('confidence', 1.0)
            })
        else:
            return jsonify({'success': False, 'error': result.get('error', 'Translation failed')}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500



# History routes
@app.route('/history')
def history():
    history = session.get('translation_history', [])
    return render_template('history.html', history=history)

@app.route('/clear_history', methods=['POST'])
def clear_history():
    session['translation_history'] = []
    session.modified = True
    flash('History cleared successfully!', 'success')
    return redirect(url_for('history'))

@app.route('/api/history/remove', methods=['POST'])
def remove_history_entry():
    try:
        data = request.json
        index = data.get('index')
        
        if 'translation_history' not in session:
            return jsonify({'success': False, 'error': 'No history found'}), 404
        
        history = session['translation_history']
        if index >= len(history):
            return jsonify({'success': False, 'error': 'Index out of range'}), 400
        
        removed = history.pop(index)
        session['translation_history'] = history
        session.modified = True
        
        return jsonify({
            'success': True,
            'message': f'Removed: {removed.get("original", "Unknown")}'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/clear-translation-history', methods=['POST'])
def clear_translation_history():
    session['translation_history'] = []
    session.modified = True
    return jsonify({'success': True, 'message': 'Translation history cleared'})

# Translation dashboard
@app.route('/translation-dashboard')
def translation_dashboard():
    lang_dist = {
        'Luganda': 13, 
        'Lusoga': 12, 
        'Runyankole': 12, 
        'Acholi': 12, 
        'Ateso': 12, 
        'Lugbara': 12, 
        'Rukiga': 12
    }

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
    return render_template('translator_about.html',
                         languages=LANGUAGES,
                         domains=DOMAINS,
                         stats=translator.get_stats())

# Health check
@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'model_loaded': translator.is_loaded if hasattr(translator, 'is_loaded') else True,
        'languages': LANGUAGES,
        'domains': DOMAINS,
        'timestamp': datetime.now().isoformat()
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# Run the app
if __name__ == '__main__':
    os.makedirs('data', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    os.makedirs('static/images', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    os.makedirs('docs', exist_ok=True)
    
    print("=" * 60)
    print("🌟 VisionLens AI - UgTalk Translator 🌟")
    print("Group C - RECESS Final Project 2026")
    print("=" * 60)
    print(f"Languages: {len(LANGUAGES)}")
    print(f"Domains: {len(DOMAINS)}")
    print("=" * 60)
    print("Server running at: http://localhost:5000")
    print("Health check: http://localhost:5000/api/health")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)