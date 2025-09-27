from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import StandardScaler
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple
import logging
from datetime import datetime, timedelta
import joblib
import os

from models.pydantic_schemas import TransactionCreate, AnomalyFactors

logger = logging.getLogger(__name__)

class AnomalyDetector:
    """
    Machine Learning anomaly detection service for fraud scoring.
    
    Uses ensemble of:
    - Isolation Forest for global anomalies  
    - Local Outlier Factor for local anomalies
    - Rule-based velocity and pattern checks
    """
    
    def __init__(self):
        self.isolation_forest = None
        self.local_outlier_factor = None
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_columns = [
            'amount', 'hour', 'day_of_week', 'merchant_frequency',
            'user_velocity', 'amount_zscore', 'category_encoded'
        ]
        
        # Model paths
        self.model_dir = "models/saved"
        os.makedirs(self.model_dir, exist_ok=True)
        
        # Initialize models
        self._initialize_models()
        
        # Try to load pre-trained models
        self._load_models()
    
    def _initialize_models(self):
        """Initialize ML models with optimal parameters"""
        # Isolation Forest - good for global anomalies
        self.isolation_forest = IsolationForest(
            contamination=0.1,  # Expect 10% anomalies
            random_state=42,
            n_estimators=100,
            max_samples='auto',
            max_features=1.0
        )
        
        # Local Outlier Factor - good for local anomalies
        self.local_outlier_factor = LocalOutlierFactor(
            n_neighbors=20,
            contamination=0.1,
            novelty=True  # For scoring new samples
        )
        
        logger.info("✅ Anomaly detection models initialized")
    
    def _load_models(self):
        """Load pre-trained models if available"""
        try:
            if os.path.exists(f"{self.model_dir}/isolation_forest.joblib"):
                self.isolation_forest = joblib.load(f"{self.model_dir}/isolation_forest.joblib")
                self.local_outlier_factor = joblib.load(f"{self.model_dir}/local_outlier_factor.joblib")
                self.scaler = joblib.load(f"{self.model_dir}/scaler.joblib")
                self.is_trained = True
                logger.info("✅ Pre-trained models loaded successfully")
        except Exception as e:
            logger.warning(f"Could not load pre-trained models: {e}")
            self._train_with_synthetic_data()
    
    def _train_with_synthetic_data(self):
        """Train models with synthetic transaction data"""
        logger.info("🎯 Training models with synthetic data...")
        
        # Generate synthetic training data
        training_data = self._generate_synthetic_data(n_samples=10000)
        
        # Train models
        self.train(training_data)
        
        logger.info("✅ Models trained with synthetic data")
    
    def _generate_synthetic_data(self, n_samples: int = 10000) -> pd.DataFrame:
        """Generate synthetic transaction data for training"""
        np.random.seed(42)
        
        # Normal transactions (90%)
        n_normal = int(n_samples * 0.9)
        normal_amounts = np.random.lognormal(mean=3, sigma=1, size=n_normal)
        
        # Anomalous transactions (10%)
        n_anomaly = n_samples - n_normal
        anomaly_amounts = np.concatenate([
            np.random.lognormal(mean=6, sigma=0.5, size=n_anomaly//2),  # High amounts
            np.random.uniform(0.01, 1, size=n_anomaly//2)  # Micro amounts
        ])
        
        amounts = np.concatenate([normal_amounts, anomaly_amounts])
        
        # Time features
        hours = np.random.randint(0, 24, n_samples)
        days_of_week = np.random.randint(0, 7, n_samples)
        
        # Merchant frequency (higher for normal, lower for anomalies)
        merchant_frequencies = np.concatenate([
            np.random.gamma(2, 10, n_normal),  # Normal merchants
            np.random.gamma(0.5, 2, n_anomaly)  # Rare merchants
        ])
        
        # User velocity (transactions per day)
        user_velocities = np.concatenate([
            np.random.gamma(2, 2, n_normal),
            np.random.gamma(5, 3, n_anomaly)  # High velocity for anomalies
        ])
        
        # Category encoding (simplified)
        categories = np.random.randint(0, 10, n_samples)
        
        data = pd.DataFrame({
            'amount': amounts,
            'hour': hours,
            'day_of_week': days_of_week,
            'merchant_frequency': merchant_frequencies,
            'user_velocity': user_velocities,
            'amount_zscore': (amounts - np.mean(amounts)) / np.std(amounts),
            'category_encoded': categories,
            'is_fraud': np.concatenate([np.zeros(n_normal), np.ones(n_anomaly)])
        })
        
        return data
    
    def train(self, training_data: pd.DataFrame) -> Dict[str, Any]:
        """Train anomaly detection models"""
        try:
            # Prepare features
            X = training_data[self.feature_columns].fillna(0)
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Train Isolation Forest
            self.isolation_forest.fit(X_scaled)
            
            # Train Local Outlier Factor
            self.local_outlier_factor.fit(X_scaled)
            
            self.is_trained = True
            
            # Save models
            self._save_models()
            
            # Calculate training metrics
            if_scores = self.isolation_forest.decision_function(X_scaled)
            lof_scores = self.local_outlier_factor.decision_function(X_scaled)
            
            training_metrics = {
                "samples_trained": len(X),
                "isolation_forest_scores": {
                    "mean": float(np.mean(if_scores)),
                    "std": float(np.std(if_scores)),
                    "min": float(np.min(if_scores)),
                    "max": float(np.max(if_scores))
                },
                "lof_scores": {
                    "mean": float(np.mean(lof_scores)),
                    "std": float(np.std(lof_scores)),
                    "min": float(np.min(lof_scores)),
                    "max": float(np.max(lof_scores))
                }
            }
            
            logger.info(f"✅ Models trained successfully on {len(X)} samples")
            return training_metrics
            
        except Exception as e:
            logger.error(f"❌ Model training failed: {e}")
            raise
    
    def _save_models(self):
        """Save trained models to disk"""
        try:
            joblib.dump(self.isolation_forest, f"{self.model_dir}/isolation_forest.joblib")
            joblib.dump(self.local_outlier_factor, f"{self.model_dir}/local_outlier_factor.joblib")
            joblib.dump(self.scaler, f"{self.model_dir}/scaler.joblib")
            logger.info("✅ Models saved successfully")
        except Exception as e:
            logger.error(f"❌ Failed to save models: {e}")
    
    async def score_transaction(self, transaction: TransactionCreate) -> float:
        """
        Calculate fraud score for a transaction.
        
        Returns:
            float: Fraud probability score (0-1)
        """
        if not self.is_trained:
            logger.warning("Models not trained, using rule-based scoring")
            return await self._rule_based_score(transaction)
        
        try:
            # Extract features
            features = await self._extract_features(transaction)
            feature_vector = np.array([[
                features['amount'],
                features['hour'],
                features['day_of_week'],
                features['merchant_frequency'],
                features['user_velocity'],
                features['amount_zscore'],
                features['category_encoded']
            ]])
            
            # Scale features
            feature_vector_scaled = self.scaler.transform(feature_vector)
            
            # Get ML scores
            if_score = self.isolation_forest.decision_function(feature_vector_scaled)[0]
            lof_score = self.local_outlier_factor.decision_function(feature_vector_scaled)[0]
            
            # Convert to probabilities (0-1)
            if_prob = self._convert_to_probability(if_score, method='isolation_forest')
            lof_prob = self._convert_to_probability(lof_score, method='lof')
            
            # Rule-based score
            rule_score = await self._rule_based_score(transaction)
            
            # Ensemble scoring with weights
            ensemble_score = (
                0.4 * if_prob +
                0.3 * lof_prob +
                0.3 * rule_score
            )
            
            # Clamp to [0, 1]
            final_score = max(0.0, min(1.0, ensemble_score))
            
            logger.info(f"Transaction scored: IF={if_prob:.3f}, LOF={lof_prob:.3f}, Rule={rule_score:.3f}, Final={final_score:.3f}")
            
            return final_score
            
        except Exception as e:
            logger.error(f"❌ Scoring failed: {e}")
            # Fallback to rule-based scoring
            return await self._rule_based_score(transaction)
    
    def _convert_to_probability(self, score: float, method: str) -> float:
        """Convert ML scores to probabilities"""
        if method == 'isolation_forest':
            # IF scores are typically in [-0.5, 0.5] range
            # Negative scores indicate anomalies
            return max(0.0, min(1.0, 0.5 - score))
        elif method == 'lof':
            # LOF scores are typically in [-1.5, 2.0] range
            # Higher scores indicate anomalies
            return max(0.0, min(1.0, (score + 1.5) / 3.5))
        else:
            return 0.5
    
    async def _extract_features(self, transaction: TransactionCreate) -> Dict[str, float]:
        """Extract ML features from transaction"""
        timestamp = transaction.timestamp or datetime.utcnow()
        
        features = {
            'amount': float(transaction.amount),
            'hour': float(timestamp.hour),
            'day_of_week': float(timestamp.weekday()),
            'merchant_frequency': await self._get_merchant_frequency(transaction.merchant_id),
            'user_velocity': await self._get_user_velocity(transaction.user_id),
            'amount_zscore': 0.0,  # Will be calculated with historical data
            'category_encoded': self._encode_category(transaction.category)
        }
        
        return features
    
    async def _get_merchant_frequency(self, merchant_id: str) -> float:
        """Get merchant transaction frequency (stub - replace with DB query)"""
        # TODO: Query database for merchant transaction count
        # For now, return a random value based on merchant_id hash
        import hashlib
        hash_val = int(hashlib.md5(merchant_id.encode()).hexdigest()[:8], 16)
        return float(hash_val % 100 + 1)
    
    async def _get_user_velocity(self, user_id: str) -> float:
        """Get user transaction velocity (transactions per day)"""
        # TODO: Query database for user's recent transaction velocity
        # For now, return a random value based on user_id hash
        import hashlib
        hash_val = int(hashlib.md5(user_id.encode()).hexdigest()[:8], 16)
        return float(hash_val % 10 + 1)
    
    def _encode_category(self, category: str) -> float:
        """Encode transaction category to numeric value"""
        if not category:
            return 0.0
        
        # Simple hash-based encoding
        import hashlib
        hash_val = int(hashlib.md5(category.lower().encode()).hexdigest()[:8], 16)
        return float(hash_val % 10)
    
    async def _rule_based_score(self, transaction: TransactionCreate) -> float:
        """Rule-based fraud scoring as fallback"""
        score = 0.0
        
        # High amount rule
        if transaction.amount > 10000:
            score += 0.3
        elif transaction.amount > 5000:
            score += 0.2
        elif transaction.amount > 1000:
            score += 0.1
        
        # Micro transaction rule
        if transaction.amount < 1:
            score += 0.2
        
        # Time-based rules
        timestamp = transaction.timestamp or datetime.utcnow()
        if timestamp.hour < 6 or timestamp.hour > 22:  # Late night/early morning
            score += 0.1
        
        # Weekend rule
        if timestamp.weekday() >= 5:  # Saturday/Sunday
            score += 0.05
        
        # Category-based rules
        high_risk_categories = ['gambling', 'cryptocurrency', 'adult', 'cash_advance']
        if transaction.category and transaction.category.lower() in high_risk_categories:
            score += 0.3
        
        return min(1.0, score)
    
    async def get_anomaly_factors(self, transaction: TransactionCreate) -> AnomalyFactors:
        """Get detailed anomaly factor breakdown"""
        features = await self._extract_features(transaction)
        
        if not self.is_trained:
            return AnomalyFactors(
                isolation_forest_score=0.0,
                local_outlier_factor=0.0,
                amount_zscore=abs(features['amount'] - 100) / 100,  # Simplified
                velocity_score=min(1.0, features['user_velocity'] / 10),
                merchant_risk=min(1.0, 1.0 / max(1, features['merchant_frequency'] / 10)),
                time_risk=0.1 if features['hour'] < 6 or features['hour'] > 22 else 0.0
            )
        
        # Get ML scores
        feature_vector = np.array([[
            features['amount'], features['hour'], features['day_of_week'],
            features['merchant_frequency'], features['user_velocity'],
            features['amount_zscore'], features['category_encoded']
        ]])
        
        feature_vector_scaled = self.scaler.transform(feature_vector)
        
        if_score = self.isolation_forest.decision_function(feature_vector_scaled)[0]
        lof_score = self.local_outlier_factor.decision_function(feature_vector_scaled)[0]
        
        return AnomalyFactors(
            isolation_forest_score=self._convert_to_probability(if_score, 'isolation_forest'),
            local_outlier_factor=self._convert_to_probability(lof_score, 'lof'),
            amount_zscore=abs(features['amount_zscore']),
            velocity_score=min(1.0, features['user_velocity'] / 10),
            merchant_risk=min(1.0, 1.0 / max(1, features['merchant_frequency'] / 10)),
            time_risk=0.1 if features['hour'] < 6 or features['hour'] > 22 else 0.0
        )