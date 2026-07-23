"""
AI-Powered Web Service - Flask Application
Group C - RECESS Final Project 2026
"""

from flask import Flask, render_template, request, jsonify, send_file
import os
import sys

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config
from models.ml_predictor import MLPredictor
from models.image_predictor import ImagePredictor

app = Flask(__name__)
app.config.from_object(Config)

# Initialize ML-based AI predictor
predictor = MLPredictor()
image_predictor = ImagePredictor()

@app.route('/')
def index():
    """Home page"""
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
    
    app.run(debug=True, host='0.0.0.0', port=5000)