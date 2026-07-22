"""
Test suite for AI-Powered Web Service
"""

import pytest
import sys
import os
import io

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models.predictor import AIPredictor

@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def predictor():
    """Create predictor instance"""
    return AIPredictor()

class TestFlaskApp:
    """Test Flask application endpoints"""
    
    def test_index_page(self, client):
        """Test home page loads"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'VisionLens AI' in response.data
    
    def test_about_page(self, client):
        """Test about page loads"""
        response = client.get('/about')
        assert response.status_code == 200
        assert b'About This Project' in response.data

    def test_product_pages(self, client):
        """Test the product information pages load"""
        for path, text in [('/models', b'Sentiment analysis'), ('/guide', b'From input to insight'), ('/history', b'Recent analyses')]:
            response = client.get(path)
            assert response.status_code == 200
            assert text in response.data
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get('/api/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'healthy'
        assert data['service'] == 'VisionLens AI'
    
    def test_predict_endpoint_success(self, client):
        """Test prediction endpoint with valid input"""
        response = client.post('/predict', 
            json={'text': 'This is a great product!', 'type': 'text'})
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == True
        assert 'result' in data
        assert 'prediction' in data['result']
        assert data['result']['prediction']['sentiment'] == 'positive'
    
    def test_predict_endpoint_empty_input(self, client):
        """Test prediction endpoint with empty input"""
        response = client.post('/predict', 
            json={'text': '', 'type': 'text'})
        assert response.status_code == 400
    
    def test_predict_endpoint_no_data(self, client):
        """Test prediction endpoint with no data"""
        response = client.post('/predict', 
            json={})
        assert response.status_code == 400

    def test_predict_endpoint_selects_text_classifier(self, client):
        """Test that the requested text model is used"""
        response = client.post('/predict', json={
            'text': 'Computer software programming code',
            'model': 'text_classification',
            'type': 'text'
        })
        assert response.status_code == 200
        data = response.get_json()
        assert data['result']['model_used'] == 'text_classification_ml'
        assert data['result']['prediction']['category'] == 'technology'

    def test_text_classifier_marks_unrelated_text_general(self, client):
        """Test that unrelated text is not forced into a topic"""
        response = client.post('/predict', json={
            'text': 'hello',
            'model': 'text_classification',
            'type': 'text'
        })
        assert response.status_code == 200
        prediction = response.get_json()['result']['prediction']
        assert prediction['category'] == 'general'
        assert 'general' in prediction['explanation']

    def test_predict_endpoint_rejects_unknown_model(self, client):
        """Test that unsupported model names are rejected"""
        response = client.post('/predict', json={
            'text': 'Test message',
            'model': 'unknown_model'
        })
        assert response.status_code == 400
        data = response.get_json()
        assert 'available_models' in data
    
    def test_models_endpoint(self, client):
        """Test models listing endpoint"""
        response = client.get('/api/models')
        assert response.status_code == 200
        data = response.get_json()
        assert 'models' in data
        assert len(data['models']) > 0

    def test_image_endpoint_requires_upload(self, client):
        """Test that image analysis requires an uploaded file"""
        response = client.post('/analyze-image')
        assert response.status_code == 400
        assert response.get_json()['error'] == 'Please upload an image'

    def test_image_endpoint_rejects_non_image(self, client):
        """Test that image analysis rejects non-image uploads"""
        response = client.post('/analyze-image', data={
            'image': (io.BytesIO(b'not an image'), 'notes.txt')
        }, content_type='multipart/form-data')
        assert response.status_code == 400
        assert response.get_json()['error'] == 'Only image files are supported'

class TestAIPredictor:
    """Test AI Predictor functionality"""
    
    def test_predictor_initialization(self, predictor):
        """Test predictor initializes correctly"""
        assert predictor is not None
        assert len(predictor.models) > 0
    
    def test_sentiment_analysis_positive(self, predictor):
        """Test positive sentiment detection"""
        result = predictor._sentiment_analyzer("This is a great and wonderful product!")
        assert result['sentiment'] == 'positive'
        assert result['positive_words'] > 0
    
    def test_sentiment_analysis_negative(self, predictor):
        """Test negative sentiment detection"""
        result = predictor._sentiment_analyzer("This is terrible and awful!")
        assert result['sentiment'] == 'negative'
        assert result['negative_words'] > 0
    
    def test_sentiment_analysis_neutral(self, predictor):
        """Test neutral sentiment detection"""
        result = predictor._sentiment_analyzer("The meeting is at 3pm")
        assert result['sentiment'] == 'neutral'
    
    def test_get_available_models(self, predictor):
        """Test getting available models"""
        models = predictor.get_available_models()
        assert isinstance(models, list)
        assert len(models) > 0
        assert 'sentiment_analysis' in models
    
    def test_get_model_info(self, predictor):
        """Test getting model information"""
        info = predictor.get_model_info('sentiment_analysis')
        assert 'name' in info
        assert 'description' in info
        assert info['name'] == 'Sentiment Analysis'

if __name__ == '__main__':
    pytest.main([__file__, '-v'])