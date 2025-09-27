"""
PaySim Scalability Test
Tests the PaySim integration with different sample sizes to find optimal balance
"""

import logging
import time
from typing import Dict, Any
import numpy as np

from paysim_integration import PaySimFraudDetector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_sample_sizes():
    """Test different sample sizes to find optimal performance/speed balance"""
    
    # Test different sample sizes
    sample_sizes = [
        10_000,    # Current (fast testing)
        50_000,    # Medium scale
        100_000,   # Large scale  
        250_000,   # Very large scale
        500_000,   # Maximum practical size
    ]
    
    results = []
    
    for sample_size in sample_sizes:
        logger.info(f"\n🧪 Testing with {sample_size:,} transactions...")
        
        try:
            start_time = time.time()
            
            # Initialize detector
            detector = PaySimFraudDetector(model_sample_size=sample_size)
            
            # Train models
            training_results = detector.train_models()
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Extract performance metrics
            ensemble_auc = 0.0
            individual_aucs = {}
            
            if 'performance' in training_results:
                ensemble_auc = training_results['performance'].get('ensemble_test_auc', 0.0)
                if 'individual_test_auc' in training_results['performance']:
                    individual_aucs = training_results['performance']['individual_test_auc']
            
            result = {
                'sample_size': sample_size,
                'duration_minutes': duration / 60,
                'ensemble_auc': ensemble_auc,
                'best_individual_auc': max(individual_aucs.values()) if individual_aucs else 0.0,
                'training_samples': training_results.get('metadata', {}).get('n_train', 0),
                'fraud_rate': training_results.get('metadata', {}).get('fraud_rate', 0.0)
            }
            
            results.append(result)
            
            logger.info(f"✅ Sample {sample_size:,}: AUC={ensemble_auc:.3f}, Time={duration/60:.1f}min")
            
        except Exception as e:
            logger.error(f"❌ Failed for sample size {sample_size:,}: {str(e)}")
            
            result = {
                'sample_size': sample_size,
                'duration_minutes': -1,
                'ensemble_auc': 0.0,
                'best_individual_auc': 0.0,
                'training_samples': 0,
                'fraud_rate': 0.0,
                'error': str(e)
            }
            results.append(result)
    
    # Print summary
    print("\n" + "="*80)
    print("📊 PAYSIM SCALABILITY TEST RESULTS")
    print("="*80)
    print(f"{'Sample Size':<12} {'Duration':<10} {'Ensemble AUC':<12} {'Best Model':<12} {'Training':<10}")
    print("-" * 80)
    
    for result in results:
        if 'error' not in result:
            print(f"{result['sample_size']:>10,} | "
                  f"{result['duration_minutes']:>8.1f}min | "
                  f"{result['ensemble_auc']:>10.3f} | "
                  f"{result['best_individual_auc']:>10.3f} | "
                  f"{result['training_samples']:>8,}")
        else:
            print(f"{result['sample_size']:>10,} | ERROR: {result['error']}")
    
    print("\n🎯 RECOMMENDATIONS:")
    
    # Find best performance/time ratio
    valid_results = [r for r in results if 'error' not in r and r['ensemble_auc'] > 0]
    
    if valid_results:
        # Calculate efficiency score (AUC per minute)
        for r in valid_results:
            r['efficiency'] = r['ensemble_auc'] / max(r['duration_minutes'], 0.1)
        
        best_efficiency = max(valid_results, key=lambda x: x['efficiency'])
        best_performance = max(valid_results, key=lambda x: x['ensemble_auc'])
        
        print(f"• Best efficiency: {best_efficiency['sample_size']:,} samples "
              f"(AUC={best_efficiency['ensemble_auc']:.3f}, {best_efficiency['duration_minutes']:.1f}min)")
        print(f"• Best performance: {best_performance['sample_size']:,} samples "
              f"(AUC={best_performance['ensemble_auc']:.3f}, {best_performance['duration_minutes']:.1f}min)")
        
        if best_efficiency['sample_size'] != best_performance['sample_size']:
            print(f"• Recommended: {best_efficiency['sample_size']:,} for development, "
                  f"{best_performance['sample_size']:,} for production")
        else:
            print(f"• Recommended: {best_efficiency['sample_size']:,} samples (optimal balance)")
    
    return results

def train_full_scale_model(sample_size: int = 500_000):
    """Train a production-scale PaySim model"""
    
    logger.info(f"\n🚀 Training production-scale PaySim model...")
    logger.info(f"📊 Sample size: {sample_size:,} transactions")
    logger.info(f"⏱️ Expected training time: 10-30 minutes")
    
    start_time = time.time()
    
    # Initialize with large sample
    detector = PaySimFraudDetector(model_sample_size=sample_size)
    
    # Train models
    results = detector.train_models()
    
    end_time = time.time()
    duration = end_time - start_time
    
    logger.info(f"\n✅ Production model training complete!")
    logger.info(f"⏱️ Training time: {duration/60:.1f} minutes")
    
    if 'performance' in results:
        perf = results['performance']
        logger.info(f"🎯 Ensemble AUC: {perf.get('ensemble_test_auc', 0.0):.3f}")
        
        if 'individual_test_auc' in perf:
            logger.info("🤖 Individual model performance:")
            for model, auc in perf['individual_test_auc'].items():
                logger.info(f"   {model}: {auc:.3f}")
    
    return detector, results

if __name__ == "__main__":
    print("🧪 PaySim Scalability Analysis")
    print("This will test different sample sizes to find the optimal balance")
    print("between model performance and training time.\n")
    
    # Test scalability
    results = test_sample_sizes()
    
    # Ask user if they want to train full-scale model
    print("\n" + "="*50)
    print("Would you like to train a production-scale model?")
    print("This will use 500,000 transactions and may take 10-30 minutes.")
    print("="*50)