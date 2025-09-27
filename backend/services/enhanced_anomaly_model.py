"""
Enhanced Anomaly Detection Model with PaySim Integration

This module provides advanced fraud detection models trained on PaySim dataset.
Includes ensemble methods, deep learning, and interpretable ML models.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple, Optional, Union
import logging
from pathlib import Path
import joblib
import json
from datetime import datetime

# ML Libraries
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.neighbors import LocalOutlierFactor
from sklearn.linear_model import LogisticRegression
from sklearn.svm import OneClassSVM
from sklearn.metrics import (
    classification_report, confusion_matrix, roc_auc_score, 
    precision_recall_curve, average_precision_score, roc_curve
)
from sklearn.model_selection import cross_val_score, StratifiedKFold
import xgboost as xgb

# Feature importance and explainability
from sklearn.inspection import permutation_importance
import shap

# Custom imports
from paysim_loader import PaySimLoader, load_paysim_for_training
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.pydantic_schemas import TransactionCreate, AnomalyFactors

logger = logging.getLogger(__name__)

class PaySimAnomalyDetector:
    """
    Advanced anomaly detection system trained on PaySim dataset
    
    Features:
    - Multiple ML models (Isolation Forest, LOF, XGBoost, etc.)
    - Ensemble predictions with confidence scoring
    - Feature importance analysis
    - SHAP explanations
    - Model interpretability
    """
    
    def __init__(self, model_dir: str = "backend/models/paysim"):
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(parents=True, exist_ok=True)
        
        # Models
        self.models = {}
        self.ensemble_weights = {}
        self.feature_names = []
        self.metadata = {}
        
        # Training history
        self.training_history = {}
        self.is_trained = False
        
        # SHAP explainer
        self.shap_explainer = None
        
        logger.info("🤖 PaySim Anomaly Detector initialized")
    
    def train_models(self, sample_size: int = 200000, 
                    balance_data: bool = True,
                    save_models: bool = True) -> Dict[str, Any]:
        """
        Train all fraud detection models on PaySim data
        
        Args:
            sample_size: Number of samples to use for training
            balance_data: Whether to balance fraud/non-fraud samples
            save_models: Whether to save trained models
            
        Returns:
            Training results and metrics
        """
        logger.info(f"🎯 Starting model training on PaySim dataset...")
        logger.info(f"   Sample size: {sample_size:,}")
        logger.info(f"   Balance data: {balance_data}")
        
        # Load and prepare data
        data_splits, metadata = load_paysim_for_training(
            sample_size=sample_size,
            balance_data=balance_data
        )
        
        self.metadata = metadata
        self.feature_names = metadata['feature_names']
        
        # Training data
        X_train = data_splits['X_train']
        y_train = data_splits['y_train']
        X_val = data_splits['X_val']
        y_val = data_splits['y_val']
        X_test = data_splits['X_test']
        y_test = data_splits['y_test']
        
        # Initialize models
        models_config = self._get_models_config()
        training_results = {}
        
        logger.info("🏗️ Training individual models...")
        
        # Train each model
        for model_name, model_config in models_config.items():
            logger.info(f"   Training {model_name}...")
            
            model = model_config['model']
            model_type = model_config['type']
            
            try:
                if model_type == 'unsupervised':
                    # Unsupervised models (anomaly detection)
                    model.fit(X_train)
                    
                    # Get anomaly scores
                    train_scores = model.decision_function(X_train)
                    val_scores = model.decision_function(X_val)
                    test_scores = model.decision_function(X_test)
                    
                    # Convert to probabilities (0-1)
                    train_probs = self._convert_anomaly_scores(train_scores, model_name)
                    val_probs = self._convert_anomaly_scores(val_scores, model_name)
                    test_probs = self._convert_anomaly_scores(test_scores, model_name)
                    
                elif model_type == 'supervised':
                    # Supervised models
                    model.fit(X_train, y_train)
                    
                    # Get probability predictions
                    train_probs = model.predict_proba(X_train)[:, 1]
                    val_probs = model.predict_proba(X_val)[:, 1]
                    test_probs = model.predict_proba(X_test)[:, 1]
                
                # Evaluate model
                val_auc = roc_auc_score(y_val, val_probs)
                test_auc = roc_auc_score(y_test, test_probs)
                val_ap = average_precision_score(y_val, val_probs)
                test_ap = average_precision_score(y_test, test_probs)
                
                # Store model and results
                self.models[model_name] = model
                training_results[model_name] = {
                    'val_auc': val_auc,
                    'test_auc': test_auc,
                    'val_ap': val_ap,
                    'test_ap': test_ap,
                    'model_type': model_type
                }
                
                logger.info(f"   ✅ {model_name}: Val AUC={val_auc:.4f}, Test AUC={test_auc:.4f}")
                
            except Exception as e:
                logger.error(f"   ❌ Failed to train {model_name}: {e}")
                continue
        
        # Calculate ensemble weights based on validation AUC
        self._calculate_ensemble_weights(training_results)
        
        # Train ensemble predictions
        ensemble_val_probs = self._ensemble_predict(X_val)
        ensemble_test_probs = self._ensemble_predict(X_test)
        
        ensemble_val_auc = roc_auc_score(y_val, ensemble_val_probs)
        ensemble_test_auc = roc_auc_score(y_test, ensemble_test_probs)
        
        training_results['ensemble'] = {
            'val_auc': ensemble_val_auc,
            'test_auc': ensemble_test_auc,
            'val_ap': average_precision_score(y_val, ensemble_val_probs),
            'test_ap': average_precision_score(y_test, ensemble_test_probs),
            'weights': self.ensemble_weights
        }
        
        logger.info(f"🎯 Ensemble: Val AUC={ensemble_val_auc:.4f}, Test AUC={ensemble_test_auc:.4f}")
        
        # Initialize SHAP explainer with best supervised model
        self._initialize_shap_explainer(X_train)
        
        # Store training history
        self.training_history = {
            'timestamp': datetime.now().isoformat(),
            'sample_size': sample_size,
            'results': training_results,
            'metadata': metadata
        }
        
        self.is_trained = True
        
        # Save models if requested
        if save_models:
            self._save_models()
        
        logger.info("🎉 Model training complete!")
        
        return training_results
    
    def _get_models_config(self) -> Dict[str, Dict]:
        """Get configuration for all models"""
        return {
            'isolation_forest': {
                'model': IsolationForest(
                    contamination=0.1,
                    n_estimators=200,
                    max_samples='auto',
                    random_state=42,
                    n_jobs=-1
                ),
                'type': 'unsupervised'
            },
            'local_outlier_factor': {
                'model': LocalOutlierFactor(
                    n_neighbors=20,
                    contamination=0.1,
                    novelty=True,
                    n_jobs=-1
                ),
                'type': 'unsupervised'
            },
            'one_class_svm': {
                'model': OneClassSVM(
                    kernel='rbf',
                    gamma='scale',
                    nu=0.1
                ),
                'type': 'unsupervised'
            },
            'xgboost': {
                'model': xgb.XGBClassifier(
                    n_estimators=200,
                    max_depth=6,
                    learning_rate=0.1,
                    subsample=0.8,
                    colsample_bytree=0.8,
                    random_state=42,
                    eval_metric='logloss',
                    use_label_encoder=False
                ),
                'type': 'supervised'
            },
            'random_forest': {
                'model': RandomForestClassifier(
                    n_estimators=200,
                    max_depth=10,
                    min_samples_split=5,
                    min_samples_leaf=2,
                    random_state=42,
                    n_jobs=-1,
                    class_weight='balanced'
                ),
                'type': 'supervised'
            },
            'logistic_regression': {
                'model': LogisticRegression(
                    C=1.0,
                    class_weight='balanced',
                    random_state=42,
                    max_iter=1000
                ),
                'type': 'supervised'
            }
        }
    
    def _convert_anomaly_scores(self, scores: np.ndarray, model_name: str) -> np.ndarray:
        """Convert anomaly scores to probabilities"""
        if model_name == 'isolation_forest':
            # IF scores are typically in [-0.5, 0.5], negative = anomaly
            return np.clip(0.5 - scores, 0, 1)
        elif model_name == 'local_outlier_factor':
            # LOF scores: higher = more anomalous
            return np.clip((scores + 2) / 4, 0, 1)
        elif model_name == 'one_class_svm':
            # SVM scores: negative = anomaly
            return np.clip(0.5 - scores, 0, 1)
        else:
            # Generic normalization
            return (scores - scores.min()) / (scores.max() - scores.min())
    
    def _calculate_ensemble_weights(self, results: Dict[str, Dict]):
        """Calculate ensemble weights based on validation AUC"""
        aucs = {name: res['val_auc'] for name, res in results.items()}
        total_auc = sum(aucs.values())
        
        # Weight by AUC performance
        self.ensemble_weights = {
            name: auc / total_auc for name, auc in aucs.items()
        }
        
        logger.info("⚖️ Ensemble weights calculated:")
        for name, weight in self.ensemble_weights.items():
            logger.info(f"   {name}: {weight:.3f}")
    
    def _ensemble_predict(self, X: np.ndarray) -> np.ndarray:
        """Make ensemble predictions"""
        predictions = []
        weights = []
        
        for model_name, model in self.models.items():
            weight = self.ensemble_weights.get(model_name, 0)
            if weight > 0:
                if hasattr(model, 'predict_proba'):
                    pred = model.predict_proba(X)[:, 1]
                else:
                    scores = model.decision_function(X)
                    pred = self._convert_anomaly_scores(scores, model_name)
                
                predictions.append(pred)
                weights.append(weight)
        
        if not predictions:
            return np.zeros(len(X))
        
        # Weighted average
        predictions = np.array(predictions)
        weights = np.array(weights)
        weights = weights / weights.sum()  # Normalize
        
        return np.average(predictions, axis=0, weights=weights)
    
    def _initialize_shap_explainer(self, X_train: np.ndarray):
        """Initialize SHAP explainer for model interpretability"""
        try:
            # Use the best supervised model for SHAP
            supervised_models = {
                name: model for name, model in self.models.items()
                if hasattr(model, 'predict_proba')
            }
            
            if supervised_models:
                # Use XGBoost if available, otherwise first available
                if 'xgboost' in supervised_models:
                    shap_model = supervised_models['xgboost']
                else:
                    shap_model = list(supervised_models.values())[0]
                
                # Sample subset for SHAP (SHAP can be slow on large datasets)
                n_background = min(1000, len(X_train))
                background_idx = np.random.choice(len(X_train), n_background, replace=False)
                background_data = X_train[background_idx]
                
                self.shap_explainer = shap.Explainer(shap_model, background_data)
                logger.info("✅ SHAP explainer initialized")
                
        except Exception as e:
            logger.warning(f"⚠️ Failed to initialize SHAP explainer: {e}")
    
    def predict(self, X: np.ndarray, return_individual: bool = False) -> Union[np.ndarray, Dict[str, np.ndarray]]:
        """
        Make fraud predictions using ensemble
        
        Args:
            X: Feature matrix
            return_individual: Whether to return individual model predictions
            
        Returns:
            Ensemble predictions or dict with individual predictions
        """
        if not self.is_trained:
            raise ValueError("Models not trained. Call train_models() first.")
        
        ensemble_pred = self._ensemble_predict(X)
        
        if return_individual:
            individual_preds = {}
            for model_name, model in self.models.items():
                if hasattr(model, 'predict_proba'):
                    individual_preds[model_name] = model.predict_proba(X)[:, 1]
                else:
                    scores = model.decision_function(X)
                    individual_preds[model_name] = self._convert_anomaly_scores(scores, model_name)
            
            return {
                'ensemble': ensemble_pred,
                'individual': individual_preds
            }
        
        return ensemble_pred
    
    def explain_prediction(self, X: np.ndarray, max_samples: int = 100) -> Dict[str, Any]:
        """
        Generate SHAP explanations for predictions
        
        Args:
            X: Feature matrix (will use first max_samples rows)
            max_samples: Maximum number of samples to explain
            
        Returns:
            Explanation data including SHAP values
        """
        if self.shap_explainer is None:
            logger.warning("SHAP explainer not available")
            return {}
        
        try:
            # Limit samples for performance
            X_explain = X[:max_samples] if len(X) > max_samples else X
            
            # Get SHAP values
            shap_values = self.shap_explainer(X_explain)
            
            # Get predictions
            predictions = self.predict(X_explain)
            
            return {
                'shap_values': shap_values.values,
                'base_values': shap_values.base_values,
                'predictions': predictions,
                'feature_names': self.feature_names,
                'n_samples': len(X_explain)
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to generate explanations: {e}")
            return {}
    
    def get_feature_importance(self) -> Dict[str, Any]:
        """Get feature importance from trained models"""
        if not self.is_trained:
            raise ValueError("Models not trained. Call train_models() first.")
        
        importance_data = {}
        
        # Get importance from tree-based models
        for model_name, model in self.models.items():
            if hasattr(model, 'feature_importances_'):
                importance_data[model_name] = {
                    'importances': model.feature_importances_.tolist(),
                    'features': self.feature_names
                }
        
        # Aggregate importance across models
        if importance_data:
            all_importances = np.array([
                data['importances'] for data in importance_data.values()
            ])
            
            avg_importance = np.mean(all_importances, axis=0)
            importance_df = pd.DataFrame({
                'feature': self.feature_names,
                'importance': avg_importance
            }).sort_values('importance', ascending=False)
            
            importance_data['aggregated'] = {
                'features': importance_df['feature'].tolist(),
                'importances': importance_df['importance'].tolist()
            }
        
        return importance_data
    
    def _save_models(self):
        """Save trained models and metadata"""
        try:
            # Save individual models
            for model_name, model in self.models.items():
                model_path = self.model_dir / f"{model_name}.joblib"
                joblib.dump(model, model_path)
            
            # Save ensemble weights
            weights_path = self.model_dir / "ensemble_weights.json"
            with open(weights_path, 'w') as f:
                json.dump(self.ensemble_weights, f, indent=2)
            
            # Save metadata
            metadata_path = self.model_dir / "metadata.json"
            with open(metadata_path, 'w') as f:
                # Convert numpy types to Python types for JSON serialization
                serializable_metadata = self._make_json_serializable(self.metadata)
                json.dump(serializable_metadata, f, indent=2)
            
            # Save feature names
            features_path = self.model_dir / "feature_names.json"
            with open(features_path, 'w') as f:
                json.dump(self.feature_names, f, indent=2)
            
            # Save training history
            history_path = self.model_dir / "training_history.json"
            with open(history_path, 'w') as f:
                serializable_history = self._make_json_serializable(self.training_history)
                json.dump(serializable_history, f, indent=2)
            
            logger.info(f"✅ Models saved to {self.model_dir}")
            
        except Exception as e:
            logger.error(f"❌ Failed to save models: {e}")
    
    def _make_json_serializable(self, obj):
        """Convert numpy types to JSON serializable types"""
        if isinstance(obj, dict):
            return {k: self._make_json_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_json_serializable(v) for v in obj]
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, (np.integer, np.floating)):
            return obj.item()
        else:
            return obj
    
    def load_models(self) -> bool:
        """Load trained models from disk"""
        try:
            # Load individual models
            model_files = list(self.model_dir.glob("*.joblib"))
            for model_path in model_files:
                model_name = model_path.stem
                if model_name != "scaler":  # Skip scaler file
                    self.models[model_name] = joblib.load(model_path)
            
            # Load ensemble weights
            weights_path = self.model_dir / "ensemble_weights.json"
            if weights_path.exists():
                with open(weights_path, 'r') as f:
                    self.ensemble_weights = json.load(f)
            
            # Load metadata
            metadata_path = self.model_dir / "metadata.json"
            if metadata_path.exists():
                with open(metadata_path, 'r') as f:
                    self.metadata = json.load(f)
            
            # Load feature names
            features_path = self.model_dir / "feature_names.json"
            if features_path.exists():
                with open(features_path, 'r') as f:
                    self.feature_names = json.load(f)
            
            if self.models and self.feature_names:
                self.is_trained = True
                logger.info(f"✅ Models loaded from {self.model_dir}")
                return True
            else:
                logger.warning("⚠️ No valid models found")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to load models: {e}")
            return False

# Integration with existing anomaly_model.py
class EnhancedAnomalyDetector:
    """
    Enhanced anomaly detector that integrates PaySim models with existing system
    """
    
    def __init__(self):
        self.paysim_detector = PaySimAnomalyDetector()
        self.feature_names = []
        self.is_trained = False
        
        # Try to load existing models
        if self.paysim_detector.load_models():
            self.feature_names = self.paysim_detector.feature_names
            self.is_trained = True
            logger.info("✅ PaySim models loaded successfully")
        else:
            logger.info("ℹ️ No existing PaySim models found - will train on first use")
    
    async def score_transaction(self, transaction: TransactionCreate) -> float:
        """
        Score transaction using PaySim-trained models
        """
        if not self.is_trained:
            logger.info("🎯 Training PaySim models on first use...")
            self.paysim_detector.train_models(sample_size=50000)
            self.feature_names = self.paysim_detector.feature_names
            self.is_trained = True
        
        try:
            # Convert transaction to features (simplified for compatibility)
            features = await self._transaction_to_features(transaction)
            
            # Make prediction
            fraud_prob = self.paysim_detector.predict(features.reshape(1, -1))[0]
            
            return float(fraud_prob)
            
        except Exception as e:
            logger.error(f"❌ PaySim scoring failed: {e}")
            # Fallback to simple rule-based scoring
            return await self._simple_rule_score(transaction)
    
    async def _transaction_to_features(self, transaction: TransactionCreate) -> np.ndarray:
        """Convert transaction to feature vector (simplified version)"""
        # This is a simplified conversion - in production, you'd want
        # to properly engineer features to match training data
        
        features = np.zeros(len(self.feature_names) if self.feature_names else 50)
        
        # Basic features that should exist
        feature_mapping = {
            'amount': transaction.amount,
            'amount_log': np.log1p(transaction.amount),
            'amount_sqrt': np.sqrt(transaction.amount),
            'hour': getattr(transaction.timestamp, 'hour', 12) if transaction.timestamp else 12,
            'business_hours': 1 if 9 <= (getattr(transaction.timestamp, 'hour', 12) if transaction.timestamp else 12) <= 17 else 0,
        }
        
        # Map features if we have feature names
        if self.feature_names:
            for i, feature_name in enumerate(self.feature_names):
                if feature_name in feature_mapping:
                    features[i] = feature_mapping[feature_name]
        else:
            # Use first few positions for basic features
            features[0] = transaction.amount
            features[1] = np.log1p(transaction.amount)
            features[2] = np.sqrt(transaction.amount)
        
        return features
    
    async def _simple_rule_score(self, transaction: TransactionCreate) -> float:
        """Fallback rule-based scoring"""
        score = 0.0
        
        # High amount
        if transaction.amount > 10000:
            score += 0.3
        elif transaction.amount > 1000:
            score += 0.1
        
        # Time-based
        if transaction.timestamp:
            hour = transaction.timestamp.hour
            if hour < 6 or hour > 22:
                score += 0.2
        
        return min(1.0, score)

if __name__ == "__main__":
    # Test PaySim integration
    logging.basicConfig(level=logging.INFO,
                       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    detector = PaySimAnomalyDetector()
    results = detector.train_models(sample_size=10000)
    
    logger.info("🎉 PaySim integration test complete!")
    for model_name, metrics in results.items():
        if isinstance(metrics, dict) and 'test_auc' in metrics:
            logger.info(f"   {model_name}: AUC = {metrics['test_auc']:.4f}")