import os #ambil os
import pickle #ambil pickle
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from flask import current_app
from datetime import datetime

class SpendingClassifier:
    def __init__(self, app=None):
        """
        Initialize classifier with optional Flask app.
        Use init_app() for proper initialization.
        """
        self.model = None
        self.scaler = None
        self.app = app
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize with Flask app context"""
        self.app = app
        with app.app_context():
            self.model_path = os.path.join(app.config['MODEL_FOLDER'], 'spending_model.pkl')
            self.scaler_path = os.path.join(app.config['MODEL_FOLDER'], 'spending_scaler.pkl')
            self.load_model()
        
    def load_model(self):
        """Load trained model and scaler from file or create new ones"""
        try:
            if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
                with open(self.model_path, 'rb') as f:
                    self.model = pickle.load(f)
                with open(self.scaler_path, 'rb') as f:
                    self.scaler = pickle.load(f)
                current_app.logger.info("Loaded existing spending model and scaler")
            else:
                self.train_default_model()
        except Exception as e:
            current_app.logger.error(f"Error loading model: {str(e)}")
            self.model = None
            self.scaler = None

    def train_default_model(self):
        """Train with default data if no model exists"""
        # Features: [total_spending, daily_avg, entertainment_ratio, weekend_ratio, essential_ratio]
        # Labels: 0 (normal), 1 (overspending)
        X = np.array([
            [1500000, 50000, 0.2, 0.3, 0.6],    # Normal
            [3500000, 120000, 0.5, 0.6, 0.3],    # Overspending
            [1200000, 40000, 0.15, 0.2, 0.7],    # Normal
            [3000000, 100000, 0.4, 0.5, 0.4],    # Overspending
            [1800000, 60000, 0.25, 0.3, 0.65],   # Normal
            [4000000, 150000, 0.6, 0.7, 0.2]     # Overspending
        ])
        y = np.array([0, 1, 0, 1, 0, 1])
        
        # Scale features
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)
        
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=5,
            random_state=42,
            class_weight='balanced'
        )
        self.model.fit(X_scaled, y)
        self.save_model()
        current_app.logger.info("Trained new default spending model")

    def save_model(self):
        """Save the trained model and scaler to file"""
        try:
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            with open(self.model_path, 'wb') as f:
                pickle.dump(self.model, f)
            with open(self.scaler_path, 'wb') as f:
                pickle.dump(self.scaler, f)
        except Exception as e:
            current_app.logger.error(f"Error saving model: {str(e)}")

    def preprocess_data(self, df):
        """Prepare expense data for prediction"""
        try:
            if df.empty:
                return None
                
            # Calculate features
            total = df['jumlah'].sum()
            daily_avg = df.groupby(df['tanggal'].dt.date)['jumlah'].sum().mean()
            
            # Category ratios
            category_totals = df.groupby('kategori')['jumlah'].sum()
            entertainment_ratio = category_totals.get('hiburan', 0) / total
            essential_ratio = (category_totals.get('makanan', 0) + 
                              category_totals.get('transportasi', 0) + 
                              category_totals.get('kuliah', 0) + 
                              category_totals.get('tagihan', 0)) / total
            
            # Weekend spending ratio
            df['is_weekend'] = df['tanggal'].dt.dayofweek >= 5
            weekend_ratio = df[df['is_weekend']]['jumlah'].sum() / total
            
            return np.array([[total, daily_avg, entertainment_ratio, weekend_ratio, essential_ratio]])
            
        except Exception as e:
            current_app.logger.error(f"Error preprocessing data: {str(e)}")
            return None

    def predict(self, df):
        """Predict spending behavior (0=normal, 1=overspending)"""
        try:
            if self.model is None or self.scaler is None:
                current_app.logger.warning("No model available for prediction")
                return {
                    'prediction': 0,
                    'probability': 0.5,
                    'error': 'Model not loaded'
                }
            
            features = self.preprocess_data(df)
            if features is None:
                return {
                    'prediction': 0,
                    'probability': 0.5,
                    'error': 'Feature calculation failed'
                }
            
            # Scale features
            features_scaled = self.scaler.transform(features)
            
            prediction = self.model.predict(features_scaled)[0]
            probability = self.model.predict_proba(features_scaled)[0][1]  # Prob of overspending
            
            return {
                'prediction': int(prediction),
                'probability': float(probability),
                'features': {
                    'total_spending': float(features[0][0]),
                    'daily_avg': float(features[0][1]),
                    'entertainment_ratio': float(features[0][2]),
                    'weekend_ratio': float(features[0][3]),
                    'essential_ratio': float(features[0][4])
                }
            }
            
        except Exception as e:
            current_app.logger.error(f"Prediction error: {str(e)}")
            return {
                'prediction': 0,
                'probability': 0.5,
                'error': str(e)
            }

    def generate_insights(self, df):
        """Generate comprehensive spending insights"""
        if df.empty:
            return {
                'spending_behavior': 'normal',
                'spending_score': 50,
                'category_analysis': {},
                'daily_patterns': {},
                'budget_health': {},
                'recommendations': []
            }
        
        # Get prediction
        prediction_result = self.predict(df)
        
        # Calculate spending score (0-100, higher is worse)
        spending_score = min(100, max(0, int(prediction_result['probability'] * 100)))
        
        # Determine behavior label
        if spending_score > 70:
            behavior = "Pengeluaran Boros"
        elif spending_score > 40:
            behavior = "Pengeluaran Sedang"
        else:
            behavior = "Pengeluaran Hemat"
        
        # Category analysis
        category_totals = df.groupby('kategori')['jumlah'].sum().sort_values(ascending=False)
        highest_category = category_totals.index[0] if len(category_totals) > 0 else None
        highest_amount = category_totals.iloc[0] if len(category_totals) > 0 else 0
        
        # Daily patterns
        daily_patterns = df.groupby('hari')['jumlah'].mean().sort_values(ascending=False)
        highest_day = daily_patterns.index[0] if len(daily_patterns) > 0 else None
        highest_day_avg = daily_patterns.iloc[0] if len(daily_patterns) > 0 else 0
        
        # Budget health (simple version)
        essential_categories = ['makanan', 'transportasi', 'kuliah', 'tagihan']
        essential_spending = df[df['kategori'].isin(essential_categories)]['jumlah'].sum()
        non_essential_spending = df[~df['kategori'].isin(essential_categories)]['jumlah'].sum()
        
        # Generate recommendations
        recommendations = []
        
        if spending_score > 70:
            recommendations.append("Anda termasuk dalam kategori boros. Pertimbangkan untuk mengurangi pengeluaran hiburan.")
        
        if highest_category == 'hiburan' and highest_amount > 500000:
            recommendations.append(f"Anda menghabiskan banyak untuk hiburan ({self.format_currency(highest_amount)}). Pertimbangkan untuk mencari alternatif hiburan yang lebih murah.")
        
        if non_essential_spending / (essential_spending + non_essential_spending) > 0.4:
            recommendations.append("Lebih dari 40% pengeluaran Anda adalah untuk hal non-esensial. Pertimbangkan untuk mengalokasikan lebih banyak untuk kebutuhan pokok.")
        
        if len(recommendations) == 0:
            recommendations.append("Pola pengeluaran Anda sehat. Pertahankan kebiasaan baik ini!")
        
        return {
            'spending_behavior': behavior,
            'spending_score': spending_score,
            'category_analysis': {
                'highest_spending': {
                    'category': highest_category,
                    'amount': highest_amount
                },
                'essential_ratio': essential_spending / (essential_spending + non_essential_spending)
            },
            'daily_patterns': {
                'highest_day': {
                    'day': highest_day,
                    'average': highest_day_avg
                }
            },
            'budget_health': {
                'essential_spending': essential_spending,
                'non_essential_spending': non_essential_spending,
                'essential_ratio': essential_spending / (essential_spending + non_essential_spending)
            },
            'recommendations': recommendations
        }

    @staticmethod
    def format_currency(amount):
        """Helper function to format currency"""
        return "Rp{:,.0f}".format(amount).replace(",", ".")
