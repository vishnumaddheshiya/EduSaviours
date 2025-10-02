#!/usr/bin/env python3
"""
Train the machine learning model for dropout prediction
This script can be run independently to train and evaluate the model
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
import os
from generate_dataset import generate_synthetic_dataset
import matplotlib.pyplot as plt
import seaborn as sns

def load_or_generate_data():
    """Load existing dataset or generate new one"""
    if os.path.exists('student_dataset.csv'):
        print("Loading existing dataset...")
        df = pd.read_csv('student_dataset.csv')
    else:
        print("No dataset found. Generating synthetic dataset...")
        df = generate_synthetic_dataset(2000, 'student_dataset.csv')
    
    return df

def preprocess_data(df):
    """Preprocess the dataset for training"""
    print("Preprocessing data...")
    
    # Define feature columns (all except Target)
    feature_columns = [col for col in df.columns if col != 'Target']
    
    X = df[feature_columns]
    y = df['Target']
    
    print(f"Features: {len(feature_columns)}")
    print(f"Samples: {len(df)}")
    print(f"Target distribution: {y.value_counts().to_dict()}")
    
    return X, y, feature_columns

def train_model(X, y, feature_columns):
    """Train the Random Forest model with hyperparameter tuning"""
    print("Training Random Forest model...")
    
    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Scale the features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Hyperparameter tuning with GridSearchCV
    print("Performing hyperparameter tuning...")
    param_grid = {
        'n_estimators': [100, 200, 300],
        'max_depth': [10, 15, 20, None],
        'min_samples_split': [2, 5, 10],
        'min_samples_leaf': [1, 2, 4],
        'max_features': ['sqrt', 'log2', None]
    }
    
    # Use a smaller grid for faster training
    param_grid_small = {
        'n_estimators': [100, 200],
        'max_depth': [10, 15, None],
        'min_samples_split': [2, 5],
        'min_samples_leaf': [1, 2]
    }
    
    rf = RandomForestClassifier(random_state=42, class_weight='balanced')
    
    # Use 3-fold CV for faster training
    grid_search = GridSearchCV(
        rf, param_grid_small, cv=3, scoring='accuracy', 
        n_jobs=-1, verbose=1
    )
    
    grid_search.fit(X_train_scaled, y_train)
    
    # Get the best model
    best_model = grid_search.best_estimator_
    print(f"Best parameters: {grid_search.best_params_}")
    print(f"Best cross-validation score: {grid_search.best_score_:.4f}")
    
    # Evaluate on test set
    y_pred = best_model.predict(X_test_scaled)
    test_accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\nTest Set Performance:")
    print(f"Accuracy: {test_accuracy:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, 
                              target_names=['Graduate', 'Dropout', 'Enrolled']))
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': feature_columns,
        'importance': best_model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print("\nTop 10 Most Important Features:")
    print(feature_importance.head(10))
    
    return best_model, scaler, feature_importance, test_accuracy

def save_model(model, scaler, feature_importance):
    """Save the trained model and related files"""
    print("Saving model and scaler...")
    
    # Create models directory
    os.makedirs('models', exist_ok=True)
    
    # Save model and scaler
    joblib.dump(model, 'models/dropout_model.pkl')
    joblib.dump(scaler, 'models/scaler.pkl')
    
    # Save feature importance
    feature_importance.to_csv('models/feature_importance.csv', index=False)
    
    print("Model saved successfully!")

def plot_results(feature_importance, test_accuracy):
    """Create visualizations of the results"""
    print("Creating visualizations...")
    
    # Create plots directory
    os.makedirs('plots', exist_ok=True)
    
    # Feature importance plot
    plt.figure(figsize=(12, 8))
    top_features = feature_importance.head(15)
    sns.barplot(data=top_features, y='feature', x='importance')
    plt.title('Top 15 Most Important Features for Dropout Prediction')
    plt.xlabel('Feature Importance')
    plt.tight_layout()
    plt.savefig('plots/feature_importance.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("Plots saved to 'plots' directory")

def evaluate_model_performance(model, scaler, X_test, y_test):
    """Detailed model evaluation"""
    print("Performing detailed model evaluation...")
    
    X_test_scaled = scaler.transform(X_test)
    y_pred = model.predict(X_test_scaled)
    y_pred_proba = model.predict_proba(X_test_scaled)
    
    # Confusion Matrix
    cm = confusion_matrix(y_test, y_pred)
    
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=['Graduate', 'Dropout', 'Enrolled'],
                yticklabels=['Graduate', 'Dropout', 'Enrolled'])
    plt.title('Confusion Matrix')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.tight_layout()
    plt.savefig('plots/confusion_matrix.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # Calculate dropout risk distribution
    dropout_proba = y_pred_proba[:, 1]  # Probability of dropout
    
    plt.figure(figsize=(10, 6))
    plt.hist(dropout_proba, bins=50, alpha=0.7, edgecolor='black')
    plt.axvline(x=0.4, color='orange', linestyle='--', label='Medium Risk Threshold')
    plt.axvline(x=0.7, color='red', linestyle='--', label='High Risk Threshold')
    plt.xlabel('Dropout Risk Probability')
    plt.ylabel('Number of Students')
    plt.title('Distribution of Dropout Risk Scores')
    plt.legend()
    plt.tight_layout()
    plt.savefig('plots/risk_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("Evaluation plots saved!")

def main():
    """Main training pipeline"""
    print("="*60)
    print("DROPOUT PREDICTION MODEL TRAINING")
    print("="*60)
    
    # Load data
    df = load_or_generate_data()
    
    # Preprocess
    X, y, feature_columns = preprocess_data(df)
    
    # Train model
    model, scaler, feature_importance, test_accuracy = train_model(X, y, feature_columns)
    
    # Save model
    save_model(model, scaler, feature_importance)
    
    # Create visualizations
    plot_results(feature_importance, test_accuracy)
    
    # Split data for evaluation
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Detailed evaluation
    evaluate_model_performance(model, scaler, X_test, y_test)
    
    print("\n" + "="*60)
    print("TRAINING COMPLETE!")
    print("="*60)
    print(f"Final Model Accuracy: {test_accuracy:.4f}")
    print("Files created:")
    print("- models/dropout_model.pkl")
    print("- models/scaler.pkl") 
    print("- models/feature_importance.csv")
    print("- plots/feature_importance.png")
    print("- plots/confusion_matrix.png")
    print("- plots/risk_distribution.png")
    print("\nYou can now run the Flask application!")

if __name__ == "__main__":
    main()
