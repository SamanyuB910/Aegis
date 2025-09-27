"""
PaySim Dataset Loader and Feature Engineering Pipeline

This module handles loading and preprocessing the PaySim dataset for fraud detection.
PaySim simulates mobile money transactions based on real-world patterns.

Dataset features:
- step: Time step (1 hour per step)
- type: Transaction type (PAYMENT, TRANSFER, CASH_OUT, CASH_IN, DEBIT)
- amount: Transaction amount
- nameOrig: Customer ID who started the transaction
- oldbalanceOrg: Initial balance before transaction
- newbalanceOrig: Customer balance after transaction
- nameDest: Recipient ID
- oldbalanceDest: Initial recipient balance
- newbalanceDest: Recipient balance after transaction
- isFraud: 1 if fraud, 0 otherwise
- isFlaggedFraud: Flags illegal attempts (large transfers >200k)
"""

import pandas as pd
import numpy as np
from typing import Tuple, Dict, List, Any, Optional
import logging
from pathlib import Path
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class PaySimLoader:
    """
    PaySim dataset loader with advanced feature engineering
    """
    
    def __init__(self, dataset_path: str = "../dataset/PS_20174392719_1491204439457_log.csv"):
        self.dataset_path = Path(dataset_path)
        self.df = None
        self.feature_columns = []
        self.target_column = 'isFraud'
        self.scalers = {}
        self.encoders = {}
        
        # Feature engineering parameters
        self.velocity_windows = [1, 3, 6, 12, 24]  # hours
        self.amount_percentiles = [25, 50, 75, 90, 95, 99]
        
        logger.info("🎯 PaySim Loader initialized")
    
    def load_dataset(self, sample_size: Optional[int] = None, 
                    balance_fraud: bool = True) -> pd.DataFrame:
        """
        Load PaySim dataset with optional sampling and balancing
        
        Args:
            sample_size: Number of samples to load (None for full dataset)
            balance_fraud: Whether to balance fraud/non-fraud samples
            
        Returns:
            Loaded and optionally balanced DataFrame
        """
        logger.info(f"📂 Loading PaySim dataset from {self.dataset_path}")
        
        try:
            # Load dataset
            if sample_size:
                # Sample random rows for faster development
                total_rows = sum(1 for _ in open(self.dataset_path)) - 1  # -1 for header
                skip_rows = sorted(np.random.choice(range(1, total_rows + 1), 
                                                  total_rows - sample_size, 
                                                  replace=False))
                self.df = pd.read_csv(self.dataset_path, skiprows=skip_rows)
                logger.info(f"📊 Loaded sample of {len(self.df):,} transactions")
            else:
                self.df = pd.read_csv(self.dataset_path)
                logger.info(f"📊 Loaded full dataset: {len(self.df):,} transactions")
            
            # Basic dataset info
            fraud_count = self.df[self.target_column].sum()
            fraud_rate = fraud_count / len(self.df) * 100
            
            logger.info(f"🚨 Fraud statistics:")
            logger.info(f"   Total fraud cases: {fraud_count:,}")
            logger.info(f"   Fraud rate: {fraud_rate:.3f}%")
            
            # Transaction type distribution
            logger.info(f"💳 Transaction types:")
            for tx_type, count in self.df['type'].value_counts().items():
                fraud_in_type = self.df[self.df['type'] == tx_type][self.target_column].sum()
                fraud_rate_type = fraud_in_type / count * 100 if count > 0 else 0
                logger.info(f"   {tx_type}: {count:,} ({fraud_rate_type:.3f}% fraud)")
            
            # Balance dataset if requested
            if balance_fraud and fraud_count > 0:
                self.df = self._balance_dataset(self.df)
                logger.info(f"⚖️ Balanced dataset: {len(self.df):,} transactions")
            
            return self.df
            
        except Exception as e:
            logger.error(f"❌ Failed to load dataset: {e}")
            raise
    
    def _balance_dataset(self, df: pd.DataFrame, 
                        fraud_ratio: float = 0.1) -> pd.DataFrame:
        """
        Balance the dataset to have a reasonable fraud ratio
        
        Args:
            df: Input DataFrame
            fraud_ratio: Desired fraud ratio (default 10%)
            
        Returns:
            Balanced DataFrame
        """
        fraud_samples = df[df[self.target_column] == 1]
        normal_samples = df[df[self.target_column] == 0]
        
        fraud_count = len(fraud_samples)
        desired_normal_count = int(fraud_count / fraud_ratio - fraud_count)
        
        # Sample normal transactions if we have too many
        if len(normal_samples) > desired_normal_count:
            normal_samples = normal_samples.sample(n=desired_normal_count, random_state=42)
        
        # Combine and shuffle
        balanced_df = pd.concat([fraud_samples, normal_samples], ignore_index=True)
        balanced_df = balanced_df.sample(frac=1, random_state=42).reset_index(drop=True)
        
        return balanced_df
    
    def engineer_features(self, df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """
        Create advanced features from PaySim data
        
        Args:
            df: DataFrame to process (uses self.df if None)
            
        Returns:
            DataFrame with engineered features
        """
        if df is None:
            df = self.df.copy()
        else:
            df = df.copy()
        
        logger.info("🔧 Engineering features from PaySim data...")
        
        # 1. Basic transaction features
        df = self._create_basic_features(df)
        
        # 2. Balance analysis features
        df = self._create_balance_features(df)
        
        # 3. Customer behavior features
        df = self._create_customer_features(df)
        
        # 4. Transaction timing features  
        df = self._create_timing_features(df)
        
        # 5. Network/relationship features
        df = self._create_network_features(df)
        
        # 6. Statistical features
        df = self._create_statistical_features(df)
        
        # Store all features (will be filtered later during ML preparation)
        self.feature_columns = [col for col in df.columns if col not in ['nameOrig', 'nameDest', self.target_column]]
        
        logger.info(f"✅ Feature engineering complete: {len(self.feature_columns)} features")
        logger.info(f"📊 Features: {self.feature_columns[:10]}...")  # Show first 10
        
        return df
    
    def _create_basic_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create basic transaction features"""
        
        # Transaction amount features
        df['amount_log'] = np.log1p(df['amount'])
        df['amount_sqrt'] = np.sqrt(df['amount'])
        df['amount_squared'] = df['amount'] ** 2
        
        # Transaction type one-hot encoding (replace original type column)
        type_dummies = pd.get_dummies(df['type'], prefix='type')
        df = df.drop('type', axis=1)  # Remove original type column
        df = pd.concat([df, type_dummies], axis=1)
        
        # Amount categories
        df['amount_category'] = pd.cut(df['amount'], 
                                     bins=[0, 100, 1000, 10000, 100000, float('inf')],
                                     labels=[0, 1, 2, 3, 4])  # Use numeric labels
        df['amount_category'] = df['amount_category'].astype(float)
        
        return df
    
    def _create_balance_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create balance-related features"""
        
        # Balance changes
        df['balance_change_orig'] = df['newbalanceOrig'] - df['oldbalanceOrg']
        df['balance_change_dest'] = df['newbalanceDest'] - df['oldbalanceDest']
        
        # Balance ratios
        df['amount_to_balance_orig'] = df['amount'] / (df['oldbalanceOrg'] + 1)
        df['amount_to_balance_dest'] = df['amount'] / (df['oldbalanceDest'] + 1)
        
        # Balance inconsistencies (potential fraud indicators)
        df['balance_inconsistent_orig'] = (
            abs(df['balance_change_orig'] + df['amount']) > 0.01
        ).astype(int)
        
        df['balance_inconsistent_dest'] = (
            abs(df['balance_change_dest'] - df['amount']) > 0.01
        ).astype(int)
        
        # Zero balance flags
        df['zero_balance_orig'] = (df['oldbalanceOrg'] == 0).astype(int)
        df['zero_balance_dest'] = (df['oldbalanceDest'] == 0).astype(int)
        df['zero_newbalance_orig'] = (df['newbalanceOrig'] == 0).astype(int)
        df['zero_newbalance_dest'] = (df['newbalanceDest'] == 0).astype(int)
        
        # Balance percentiles
        df['balance_orig_pct'] = df['oldbalanceOrg'].rank(pct=True)
        df['balance_dest_pct'] = df['oldbalanceDest'].rank(pct=True)
        
        return df
    
    def _create_customer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create customer behavior features"""
        
        # Customer transaction frequency
        orig_counts = df['nameOrig'].value_counts()
        dest_counts = df['nameDest'].value_counts()
        
        df['orig_frequency'] = df['nameOrig'].map(orig_counts)
        df['dest_frequency'] = df['nameDest'].map(dest_counts)
        
        # Customer transaction amounts
        orig_amounts = df.groupby('nameOrig')['amount'].agg(['mean', 'std', 'min', 'max'])
        dest_amounts = df.groupby('nameDest')['amount'].agg(['mean', 'std', 'min', 'max'])
        
        df['orig_amount_mean'] = df['nameOrig'].map(orig_amounts['mean']).fillna(0)
        df['orig_amount_std'] = df['nameOrig'].map(orig_amounts['std']).fillna(0)
        df['dest_amount_mean'] = df['nameDest'].map(dest_amounts['mean']).fillna(0)
        df['dest_amount_std'] = df['nameDest'].map(dest_amounts['std']).fillna(0)
        
        # Amount deviation from customer's typical behavior
        df['amount_deviation_orig'] = abs(df['amount'] - df['orig_amount_mean']) / (df['orig_amount_std'] + 1)
        df['amount_deviation_dest'] = abs(df['amount'] - df['dest_amount_mean']) / (df['dest_amount_std'] + 1)
        
        return df
    
    def _create_timing_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create timing-based features"""
        
        # Time-based features
        df['hour'] = df['step'] % 24
        df['day'] = df['step'] // 24
        df['week'] = df['day'] // 7
        
        # Cyclical time features
        df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
        df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
        df['day_sin'] = np.sin(2 * np.pi * df['day'] / 7)
        df['day_cos'] = np.cos(2 * np.pi * df['day'] / 7)
        
        # Business hours
        df['business_hours'] = ((df['hour'] >= 9) & (df['hour'] <= 17)).astype(int)
        df['weekend'] = (df['day'] % 7 >= 5).astype(int)
        df['night_time'] = ((df['hour'] >= 22) | (df['hour'] <= 6)).astype(int)
        
        return df
    
    def _create_network_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create network/relationship features"""
        
        # Customer interaction patterns
        customer_pairs = df.groupby(['nameOrig', 'nameDest']).size().reset_index(name='interaction_count')
        pair_key = df['nameOrig'] + '_' + df['nameDest']
        df['customer_pair_frequency'] = pair_key.map(
            dict(zip(customer_pairs['nameOrig'] + '_' + customer_pairs['nameDest'], 
                    customer_pairs['interaction_count']))
        ).fillna(1)
        
        # Unique partners count
        orig_partners = df.groupby('nameOrig')['nameDest'].nunique()
        dest_partners = df.groupby('nameDest')['nameOrig'].nunique()
        
        df['orig_unique_partners'] = df['nameOrig'].map(orig_partners).fillna(1)
        df['dest_unique_partners'] = df['nameDest'].map(dest_partners).fillna(1)
        
        return df
    
    def _create_statistical_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create statistical features"""
        
        # Amount percentiles and z-scores
        for pct in [25, 50, 75, 90, 95, 99]:
            percentile_val = np.percentile(df['amount'], pct)
            df[f'amount_above_p{pct}'] = (df['amount'] > percentile_val).astype(int)
        
        # Z-scores
        amount_mean = df['amount'].mean()
        amount_std = df['amount'].std()
        df['amount_zscore'] = (df['amount'] - amount_mean) / amount_std
        df['amount_zscore_abs'] = abs(df['amount_zscore'])
        
        # Statistical flags
        df['amount_extreme'] = (abs(df['amount_zscore']) > 3).astype(int)
        df['amount_very_high'] = (df['amount_zscore'] > 2).astype(int)
        df['amount_very_low'] = (df['amount_zscore'] < -2).astype(int)
        
        return df
    
    def prepare_ml_data(self, test_size: float = 0.2, 
                       validation_size: float = 0.1,
                       random_state: int = 42) -> Tuple[Dict[str, np.ndarray], Dict[str, Any]]:
        """
        Prepare data for machine learning
        
        Args:
            test_size: Proportion of data for testing
            validation_size: Proportion of data for validation
            random_state: Random seed for reproducibility
            
        Returns:
            Tuple of (data_splits, metadata)
        """
        if self.df is None:
            raise ValueError("Dataset not loaded. Call load_dataset() first.")
            
        logger.info("🎯 Preparing data for machine learning...")
        
        # Get features and target
        # Remove identifier columns and target to get features
        id_columns = ['nameOrig', 'nameDest']
        columns_to_drop = id_columns + [self.target_column]
        columns_to_drop = [col for col in columns_to_drop if col in self.df.columns]
        
        feature_df = self.df.drop(columns=columns_to_drop)
        target = self.df[self.target_column]
        
        # Ensure all features are numeric
        for column in feature_df.columns:
            if feature_df[column].dtype == 'object':
                logger.warning(f"Non-numeric column found: {column}, attempting to convert...")
                try:
                    feature_df[column] = pd.to_numeric(feature_df[column], errors='coerce')
                except:
                    logger.warning(f"Could not convert {column}, dropping it...")
                    feature_df = feature_df.drop(column, axis=1)
        
        # Update feature columns list
        self.feature_columns = feature_df.columns.tolist()
        
        # Handle missing values
        feature_df = feature_df.fillna(0)
        
        logger.info(f"Final feature matrix shape: {feature_df.shape}")
        logger.info(f"Feature types: {feature_df.dtypes.value_counts()}")
        
        # Split data
        X_temp, X_test, y_temp, y_test = train_test_split(
            feature_df, target, test_size=test_size, 
            stratify=target, random_state=random_state
        )
        
        val_size_adjusted = validation_size / (1 - test_size)
        X_train, X_val, y_train, y_val = train_test_split(
            X_temp, y_temp, test_size=val_size_adjusted,
            stratify=y_temp, random_state=random_state
        )
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_val_scaled = scaler.transform(X_val)
        X_test_scaled = scaler.transform(X_test)
        
        # Store scaler for later use
        self.scalers['standard'] = scaler
        
        # Prepare data splits
        data_splits = {
            'X_train': X_train_scaled,
            'X_val': X_val_scaled,
            'X_test': X_test_scaled,
            'y_train': y_train.values,
            'y_val': y_val.values,
            'y_test': y_test.values,
            'X_train_raw': X_train.values,
            'X_val_raw': X_val.values,
            'X_test_raw': X_test.values
        }
        
        # Metadata
        metadata = {
            'feature_names': self.feature_columns,
            'n_features': len(self.feature_columns),
            'n_train': len(X_train),
            'n_val': len(X_val),
            'n_test': len(X_test),
            'fraud_rate_train': y_train.mean(),
            'fraud_rate_val': y_val.mean(),
            'fraud_rate_test': y_test.mean(),
            'scaler': scaler,
            'dataset_info': {
                'total_samples': len(self.df),
                'total_features': len(self.feature_columns),
                'fraud_samples': target.sum(),
                'normal_samples': len(target) - target.sum()
            }
        }
        
        logger.info(f"✅ Data preparation complete:")
        logger.info(f"   Training: {len(X_train):,} samples ({y_train.mean()*100:.2f}% fraud)")
        logger.info(f"   Validation: {len(X_val):,} samples ({y_val.mean()*100:.2f}% fraud)")
        logger.info(f"   Testing: {len(X_test):,} samples ({y_test.mean()*100:.2f}% fraud)")
        logger.info(f"   Features: {len(self.feature_columns)}")
        
        return data_splits, metadata
    
    def get_feature_importance_data(self) -> Dict[str, Any]:
        """Get data for feature importance analysis"""
        if not self.feature_columns:
            raise ValueError("Features not engineered. Call engineer_features() first.")
            
        return {
            'feature_names': self.feature_columns,
            'feature_groups': {
                'basic': [f for f in self.feature_columns if any(x in f for x in ['amount', 'type'])],
                'balance': [f for f in self.feature_columns if 'balance' in f],
                'customer': [f for f in self.feature_columns if any(x in f for x in ['orig', 'dest', 'frequency'])],
                'timing': [f for f in self.feature_columns if any(x in f for x in ['hour', 'day', 'week', 'time'])],
                'network': [f for f in self.feature_columns if any(x in f for x in ['partner', 'interaction'])],
                'statistical': [f for f in self.feature_columns if any(x in f for x in ['zscore', 'pct', 'percentile'])]
            }
        }

def load_paysim_for_training(sample_size: int = 100000, 
                           balance_data: bool = True) -> Tuple[Dict[str, np.ndarray], Dict[str, Any]]:
    """
    Convenience function to load and prepare PaySim data for training
    
    Args:
        sample_size: Number of samples to load (None for full dataset)
        balance_data: Whether to balance fraud/non-fraud samples
        
    Returns:
        Tuple of (data_splits, metadata)
    """
    loader = PaySimLoader()
    
    # Load dataset
    loader.load_dataset(sample_size=sample_size, balance_fraud=balance_data)
    
    # Engineer features
    loader.engineer_features()
    
    # Prepare for ML
    return loader.prepare_ml_data()

if __name__ == "__main__":
    # Test the loader
    logging.basicConfig(level=logging.INFO, 
                       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    logger.info("🧪 Testing PaySim Loader...")
    
    # Load small sample for testing
    data_splits, metadata = load_paysim_for_training(sample_size=10000)
    
    logger.info("✅ PaySim Loader test complete!")
    logger.info(f"📊 Loaded {metadata['n_train'] + metadata['n_val'] + metadata['n_test']:,} samples")
    logger.info(f"🎯 {metadata['n_features']} features engineered")