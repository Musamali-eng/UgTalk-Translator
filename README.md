# 🌍 UgTalk - AI-Powered Ugandan Language Translator

> An AI-powered web service that translates English text into 7 Ugandan languages using Machine Learning and Flask.

---

## 📋 Table of Contents
- [Project Overview](#project-overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Dataset](#dataset)
- [Installation](#installation)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)
- [Team Members](#team-members)
- [License](#license)

---

## 📖 Project Overview

**UgTalk** is an AI-Powered Web Service built with Flask that translates English text into multiple Ugandan languages. The system uses a hybrid approach combining:

- **TF-IDF Vectorization** for text representation
- **Nearest Neighbors** for similarity matching
- **Dictionary-based translations** for common phrases
- **Machine Learning models** trained on the Language Translation Dataset

### Supported Languages
| # | Language | Native Name |
|---|----------|-------------|
| 1 | Luganda | Oluganda |
| 2 | Lusoga | Olusoga |
| 3 | Runyankole | Orunyankole |
| 4 | Ateso | Ateso |
| 5 | Lugbara | Lugbara |
| 6 | Acholi | Acholi |
| 7 | Rukiga | Rukiga |

---

## ✨ Features

- ✅ **Real-time Translation** - Instant translations with confidence scores
- ✅ **7 Ugandan Languages** - Support for major Ugandan languages
- ✅ **Domain Filtering** - Filter translations by domain (Health, Tourism, Business, etc.)
- ✅ **Translation History** - Track all your translations
- ✅ **Analytics Dashboard** - Visual insights from the dataset
- ✅ **RESTful API** - Integration-ready API endpoints
- ✅ **Responsive Design** - Works on desktop and mobile
- ✅ **Interactive UI** - User-friendly interface with Bootstrap 5

---

## 🛠️ Technology Stack

### Backend
| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.9+ | Programming Language |
| Flask | 2.2.3 | Web Framework |
| Scikit-learn | 1.2.2 | Machine Learning |
| Pandas | 1.5.3 | Data Processing |
| NumPy | 1.24.3 | Numerical Computing |
| Joblib | 1.2.0 | Model Serialization |

### Frontend
| Technology | Version | Purpose |
|------------|---------|---------|
| Bootstrap | 5.3.0 | UI Framework |
| Chart.js | 4.4.0 | Data Visualization |
| Font Awesome | 6.4.0 | Icons |

### Development
| Technology | Version | Purpose |
|------------|---------|---------|
| Jupyter | 1.0.0 | Notebooks |
| Matplotlib | 3.7.1 | Visualizations |
| Seaborn | 0.12.2 | Statistical Visuals |
| Plotly | 5.14.1 | Interactive Charts |

---

## 📊 Dataset

### Source
Dataset: `Language_translation_models_dataset.csv`
Download from: [https://ryeko.org/datasets/](https://ryeko.org/datasets/)

### Statistics
| Metric | Value |
|--------|-------|
| Total Records | 2,000+ |
| Languages | 7 |
| Domains | 7 |
| Formality Levels | 2 |
| Regions | 5 |

### Data Structure
| Column | Description |
|--------|-------------|
| Sentence_ID | Unique identifier |
| Source_Language | English |
| Target_Language | Ugandan language |
| Source_Text | English text |
| Target_Text | Translated text |
| Domain | Text category |
| Formality | Formal/Informal |
| Speaker_Region | Region of origin |

---

## 🚀 Installation

### Prerequisites
- Python 3.9 or higher
- pip (Python package manager)
- Git

### Step 1: Clone the Repository
```bash
git clone https://github.com/yourusername/UgTalk-Translator.git
cd UgTalk-Translator