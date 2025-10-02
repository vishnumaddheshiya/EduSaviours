# AI-Based Dropout Prediction & Counseling System

## Overview
A comprehensive web application that predicts student dropout risk using machine learning and provides actionable insights for educational institutions.

## Features
- **Predictive Analytics**: Random Forest model for dropout prediction
- **Student Dashboard**: Individual risk assessment and recommendations
- **University Dashboard**: Institution-wide analytics and at-risk student monitoring
- **Real-time Notifications**: Automated alerts for counselors and mentors
- **Data Visualization**: Interactive charts and statistics
- **Multi-user Support**: Separate interfaces for students, counselors, and administrators

## Technology Stack
- **Backend**: Flask (Python)
- **Frontend**: Vue.js 3 (CDN)
- **Machine Learning**: Scikit-learn (Random Forest Classifier)
- **Database**: SQLite (development) / PostgreSQL (production)
- **Styling**: Bootstrap 5 + Custom CSS

## Dataset Features
The model uses 35 key features including:
- Demographics (Age, Gender, Marital status, Nationality)
- Academic Performance (Curricular units, grades, evaluations)
- Financial Status (Tuition fees, scholarship, debtor status)
- Socioeconomic Factors (Parents' education/occupation, unemployment rate)
- Institutional Data (Application mode, course type, attendance)

## Installation & Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd dropout-prediction-system
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Initialize database**
```bash
python init_db.py
```

5. **Run the application**
```bash
python app.py
```

6. **Access the application**
- Open browser and navigate to `http://localhost:5000`

## API Endpoints
- `POST /api/predict` - Predict dropout risk for a student
- `GET /api/students` - Get all students data
- `GET /api/student/<id>` - Get specific student data
- `POST /api/student` - Add new student
- `GET /api/analytics` - Get system analytics
- `POST /api/login` - User authentication

## Model Performance
- **Algorithm**: Random Forest Classifier
- **Accuracy**: ~85-90% (typical for educational datasets)
- **Features**: 35 input features
- **Output**: Risk probability (0-1) and risk category (Low/Medium/High)

## Usage
1. **For Students**: Login to view personal risk assessment and recommendations
2. **For Counselors**: Monitor at-risk students and receive notifications
3. **For Administrators**: View institution-wide analytics and trends

## Contributing
1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## License
MIT License
