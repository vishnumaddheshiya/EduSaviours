import numpy as np
import joblib
import os

class DropoutPredictor:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.feature_names = [
            'Marital status', 'Application mode', 'Application order', 'Course',
            'Daytime/evening attendance', 'Previous qualification', 'Nacionality',
            "Mother's qualification", "Father's qualification", "Mother's occupation",
            "Father's occupation", 'Displaced', 'Educational special needs', 'Debtor',
            'Tuition fees up to date', 'Gender', 'Scholarship holder', 'Age at enrollment',
            'International', 'Curricular units 1st sem (credited)',
            'Curricular units 1st sem (enrolled)', 'Curricular units 1st sem (evaluations)',
            'Curricular units 1st sem (approved)', 'Curricular units 1st sem (grade)',
            'Curricular units 1st sem (without evaluations)', 'Curricular units 2nd sem (credited)',
            'Curricular units 2nd sem (enrolled)', 'Curricular units 2nd sem (evaluations)',
            'Curricular units 2nd sem (approved)', 'Curricular units 2nd sem (grade)',
            'Curricular units 2nd sem (without evaluations)', 'Unemployment rate',
            'Inflation rate', 'GDP'
        ]

        # Load trained model
        self.load_model()

    def load_model(self):
        """Load an already-trained model and scaler"""
        try:
            self.model = joblib.load('models/dropout_model.pkl')
            self.scaler = joblib.load('models/scaler.pkl')
            print("✅ Model and scaler loaded successfully")
        except FileNotFoundError:
            raise RuntimeError(
                "❌ Model not found. Please train it first using train_model.py"
            )

    def predict(self, features):
        """
        Predict dropout risk
        Args:
            features: List of 34 feature values
        Returns:
            (risk_score, risk_category, recommendations)
        """
        if self.model is None or self.scaler is None:
            raise ValueError("Model not loaded")

        features = np.array(features).reshape(1, -1)
        features_scaled = self.scaler.transform(features)
        probabilities = self.model.predict_proba(features_scaled)[0]

        dropout_prob = probabilities[1] if len(probabilities) > 1 else 0

        if dropout_prob >= 0.7:
            risk_category = "High"
        elif dropout_prob >= 0.4:
            risk_category = "Medium"
        else:
            risk_category = "Low"

        return dropout_prob, risk_category, []
