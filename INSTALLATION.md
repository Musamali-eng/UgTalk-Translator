# Installation Guide - AI-Powered Web Service

## Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.8 or higher
- pip (Python package manager)
- Git (for version control)

## Installation Steps

### 1. Clone the Repository

```bash
git clone <repository-url>
cd ai-web-service
```

### 2. Create Virtual Environment (Recommended)

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables (Optional)

Create a `.env` file in the root directory:
```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///data/app.db
MODEL_PATH=data/models/
```

### 5. Create Required Directories

```bash
mkdir -p data/models data/uploads logs
```

### 6. Run the Application

```bash
python app.py
```

The application will start at `http://localhost:5000`

## Running Tests

To run the test suite:

```bash
# Using pytest directly
pytest tests/test_app.py -v

# Or using the test runner script
python run_tests.py
```

## Project Structure

```
ai-web-service/
├── app.py                 # Main Flask application
├── config.py             # Configuration settings
├── requirements.txt      # Python dependencies
├── models/               # AI models
│   ├── __init__.py
│   └── predictor.py
├── static/               # Static files
│   ├── css/
│   ├── js/
│   └── images/
├── templates/            # HTML templates
│   ├── base.html
│   ├── index.html
│   └── about.html
├── data/                 # Data and models
├── tests/                # Test files
├── docs/                 # Documentation
└── README.md
```

## API Endpoints

### GET /
Home page with sentiment analysis interface

### GET /about
About page with project information

### POST /predict
Predict sentiment from text input

**Request Body:**
```json
{
    "text": "Your text here",
    "type": "text"
}
```

**Response:**
```json
{
    "success": true,
    "result": {
        "sentiment": "positive",
        "score": 0.8,
        "confidence": 0.9,
        "positive_words": 3,
        "negative_words": 0
    }
}
```

### GET /api/health
Health check endpoint

### GET /api/models
List available AI models

## Troubleshooting

### Port Already in Use
If port 5000 is already in use, you can change it in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

### Module Not Found Error
Ensure you're in the correct directory and virtual environment is activated:
```bash
cd ai-web-service
venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # macOS/Linux
```

### Database Errors
Delete existing database and let Flask recreate it:
```bash
rm data/app.db  # On Unix
del data\app.db  # On Windows
```

## Development

### Code Style
- Follow PEP 8 guidelines
- Use meaningful variable names
- Add comments for complex logic
- Write docstrings for functions

### Adding New Features
1. Create a new branch: `git checkout -b feature-name`
2. Make changes and test
3. Commit changes: `git commit -m "Add feature-name"`
4. Push to repository: `git push origin feature-name`
5. Create pull request

## Deployment

### Using Gunicorn (Production)
```bash
pip install gunicorn
gunicorn -w 4 app:app
```

### Using Docker
Create a `Dockerfile`:
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "-w", "4", "app:app"]
```

Build and run:
```bash
docker build -t ai-web-service .
docker run -p 5000:5000 ai-web-service
```

## Support

For issues or questions:
- Check the documentation
- Review the project report
- Contact team members

## License

This project is developed for educational purposes as part of RECESS Final Project 2026.