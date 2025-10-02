#!/usr/bin/env python3
"""
Main entry point for the Dropout Prediction System
This script handles the complete setup and running of the application
"""

import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("Checking dependencies...")
    
    required_packages = [
        'flask', 'flask-sqlalchemy', 'flask-cors', 'flask-login',
        'scikit-learn', 'pandas', 'numpy', 'joblib', 'werkzeug',
        'python-dotenv', 'email-validator', 'bcrypt', 'apscheduler'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"Missing packages: {', '.join(missing_packages)}")
        print("Installing missing packages...")
        
        try:
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install'
            ] + missing_packages)
            print("Dependencies installed successfully!")
        except subprocess.CalledProcessError:
            print("Failed to install dependencies. Please run:")
            print(f"pip install {' '.join(missing_packages)}")
            return False
    else:
        print("All dependencies are installed!")
    
    return True

def setup_database():
    """Initialize the database if it doesn't exist"""
    db_file = Path('dropout_prediction.db')
    
    if not db_file.exists():
        print("Database not found. Initializing...")
        try:
            from init_db import main as init_db_main
            init_db_main()
            print("Database initialized successfully!")
        except Exception as e:
            print(f"Error initializing database: {e}")
            return False
    else:
        print("Database already exists.")
    
    return True

def setup_ml_model():
    """Set up the machine learning model"""
    model_file = Path('models/dropout_model.pkl')
    
    if not model_file.exists():
        print("ML model not found. Training new model...")
        try:
            from train_model import main as train_model_main
            train_model_main()
            print("Model trained successfully!")
        except Exception as e:
            print(f"Error training model: {e}")
            print("The application will use a basic model for demonstration.")
    else:
        print("ML model already exists.")
    
    return True

def create_directories():
    """Create necessary directories"""
    directories = ['models', 'plots', 'static', 'static/css', 'static/js']
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("Directories created.")

def run_application():
    """Run the Flask application"""
    print("\n" + "="*60)
    print("STARTING DROPOUT PREDICTION SYSTEM")
    print("="*60)
    
    try:
        from app import app
        print("Flask application starting...")
        print("Access the application at: http://localhost:5000")
        print("\nDefault login credentials:")
        print("- Admin: admin / admin123")
        print("- Counselor: counselor / counselor123") 
        print("- Student: student / student123")
        print("\nPress Ctrl+C to stop the server")
        print("-" * 60)
        
        app.run(debug=True, host='0.0.0.0', port=5000)
        
    except KeyboardInterrupt:
        print("\nApplication stopped by user.")
    except Exception as e:
        print(f"Error running application: {e}")

def main():
    """Main setup and run function"""
    print("DROPOUT PREDICTION SYSTEM SETUP")
    print("=" * 50)
    
    # Create directories
    create_directories()
    
    # Check dependencies
    if not check_dependencies():
        print("Please install dependencies and try again.")
        return
    
    # Setup database
    if not setup_database():
        print("Database setup failed. Please check the error and try again.")
        return
    
    # Setup ML model
    setup_ml_model()
    
    # Run application
    run_application()

if __name__ == "__main__":
    main()
