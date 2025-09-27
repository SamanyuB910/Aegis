"""
Database initialization script for FraudX+ Copilot.

This script sets up the SQLite database with all required tables
and initial data for the fraud detection system.
"""

import asyncio
import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Dict, Any
import random
import json

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = "sqlite:///./fraudx_copilot.db"

def create_database_tables():
    """Create all database tables using raw SQL"""
    
    conn = sqlite3.connect("fraudx_copilot.db")
    cursor = conn.cursor()
    
    logger.info("🗃️ Creating database tables...")
    
    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            phone TEXT,
            address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE,
            risk_score REAL DEFAULT 0.0,
            total_transactions INTEGER DEFAULT 0,
            total_spent REAL DEFAULT 0.0,
            account_flags TEXT DEFAULT '[]'
        )
    """)
    
    # Merchants table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS merchants (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT,
            address TEXT,
            phone TEXT,
            email TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE,
            risk_score REAL DEFAULT 0.0,
            transaction_count INTEGER DEFAULT 0,
            total_volume REAL DEFAULT 0.0,
            reputation REAL DEFAULT 1.0,
            flags TEXT DEFAULT '[]'
        )
    """)
    
    # Transactions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            merchant_id TEXT NOT NULL,
            amount REAL NOT NULL,
            currency TEXT DEFAULT 'USD',
            transaction_type TEXT NOT NULL,
            status TEXT DEFAULT 'completed',
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            description TEXT,
            metadata TEXT DEFAULT '{}',
            fraud_score REAL DEFAULT 0.0,
            is_flagged BOOLEAN DEFAULT FALSE,
            flagged_reasons TEXT DEFAULT '[]',
            reviewed BOOLEAN DEFAULT FALSE,
            reviewer_id TEXT,
            review_notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (merchant_id) REFERENCES merchants (id)
        )
    """)
    
    # Receipts table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS receipts (
            id TEXT PRIMARY KEY,
            transaction_id TEXT NOT NULL,
            original_filename TEXT NOT NULL,
            file_path TEXT NOT NULL,
            file_size INTEGER,
            mime_type TEXT,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ocr_text TEXT,
            ocr_confidence REAL,
            extracted_data TEXT DEFAULT '{}',
            forgery_score REAL DEFAULT 0.0,
            is_forgery BOOLEAN DEFAULT FALSE,
            analysis_complete BOOLEAN DEFAULT FALSE,
            processing_errors TEXT DEFAULT '[]',
            FOREIGN KEY (transaction_id) REFERENCES transactions (id)
        )
    """)
    
    # Merchant nodes table (for graph analysis)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS merchant_nodes (
            id TEXT PRIMARY KEY,
            merchant_id TEXT NOT NULL,
            centrality_score REAL DEFAULT 0.0,
            clustering_coefficient REAL DEFAULT 0.0,
            pagerank_score REAL DEFAULT 0.0,
            community_id TEXT,
            node_risk_score REAL DEFAULT 0.0,
            connection_count INTEGER DEFAULT 0,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            metadata TEXT DEFAULT '{}',
            FOREIGN KEY (merchant_id) REFERENCES merchants (id)
        )
    """)
    
    # Flag events table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS flag_events (
            id TEXT PRIMARY KEY,
            transaction_id TEXT NOT NULL,
            flag_type TEXT NOT NULL,
            flag_reason TEXT NOT NULL,
            confidence_score REAL NOT NULL,
            flagged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            flagged_by TEXT DEFAULT 'system',
            additional_data TEXT DEFAULT '{}',
            is_resolved BOOLEAN DEFAULT FALSE,
            resolved_at TIMESTAMP,
            resolved_by TEXT,
            resolution_notes TEXT,
            FOREIGN KEY (transaction_id) REFERENCES transactions (id)
        )
    """)
    
    # Spell runs table (for fraud simulations)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS spell_runs (
            id TEXT PRIMARY KEY,
            spell_type TEXT NOT NULL,
            parameters TEXT NOT NULL,
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            status TEXT DEFAULT 'running',
            results TEXT DEFAULT '{}',
            affected_transactions INTEGER DEFAULT 0,
            flagged_transactions INTEGER DEFAULT 0,
            total_impact REAL DEFAULT 0.0,
            error_message TEXT,
            created_by TEXT DEFAULT 'system'
        )
    """)
    
    # Create indexes for better performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_merchant_id ON transactions(merchant_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_timestamp ON transactions(timestamp)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_fraud_score ON transactions(fraud_score)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_is_flagged ON transactions(is_flagged)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_receipts_transaction_id ON receipts(transaction_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_flag_events_transaction_id ON flag_events(transaction_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_merchant_nodes_merchant_id ON merchant_nodes(merchant_id)")
    
    conn.commit()
    conn.close()
    
    logger.info("✅ Database tables created successfully")

def seed_initial_data():
    """Seed database with initial test data"""
    
    conn = sqlite3.connect("fraudx_copilot.db")
    cursor = conn.cursor()
    
    logger.info("🌱 Seeding initial data...")
    
    # Sample users
    users_data = [
        ("USER_0001", "alice.johnson@email.com", "Alice Johnson", "+1-555-0101", "123 Main St, City, State"),
        ("USER_0002", "bob.smith@email.com", "Bob Smith", "+1-555-0102", "456 Oak Ave, City, State"),
        ("USER_0003", "carol.davis@email.com", "Carol Davis", "+1-555-0103", "789 Pine St, City, State"),
        ("USER_0004", "david.wilson@email.com", "David Wilson", "+1-555-0104", "321 Elm St, City, State"),
        ("USER_0005", "eva.brown@email.com", "Eva Brown", "+1-555-0105", "654 Maple Ave, City, State"),
        ("USER_0006", "frank.miller@email.com", "Frank Miller", "+1-555-0106", "987 Cedar St, City, State"),
        ("USER_0007", "grace.taylor@email.com", "Grace Taylor", "+1-555-0107", "147 Birch Ave, City, State"),
        ("USER_0008", "henry.jones@email.com", "Henry Jones", "+1-555-0108", "258 Spruce St, City, State"),
        ("USER_0009", "iris.white@email.com", "Iris White", "+1-555-0109", "369 Walnut Ave, City, State"),
        ("USER_0010", "jack.black@email.com", "Jack Black", "+1-555-0110", "741 Cherry St, City, State")
    ]
    
    for user_data in users_data:
        cursor.execute("""
            INSERT OR IGNORE INTO users (id, email, full_name, phone, address, risk_score)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (*user_data, random.uniform(0.1, 0.8)))
    
    # Sample merchants
    merchants_data = [
        ("MERCHANT_0001", "TechGear Store", "Electronics", "1000 Tech Blvd, Tech City, State", "+1-555-1001", "info@techgear.com"),
        ("MERCHANT_0002", "Fashion Hub", "Clothing", "2000 Style Ave, Fashion District, State", "+1-555-1002", "contact@fashionhub.com"),
        ("MERCHANT_0003", "GreenGrocer Market", "Groceries", "3000 Fresh St, Market Town, State", "+1-555-1003", "orders@greengrocer.com"),
        ("MERCHANT_0004", "AutoParts Express", "Automotive", "4000 Motor Way, Auto City, State", "+1-555-1004", "sales@autoparts.com"),
        ("MERCHANT_0005", "BookWorm Library", "Books", "5000 Reading Rd, Library Hill, State", "+1-555-1005", "info@bookworm.com"),
        ("MERCHANT_0006", "SportZone Equipment", "Sports", "6000 Athletic Ave, Sports Town, State", "+1-555-1006", "gear@sportzone.com"),
        ("MERCHANT_0007", "HomeDecor Palace", "Home & Garden", "7000 Design Dr, Decor City, State", "+1-555-1007", "sales@homedecor.com"),
        ("MERCHANT_0008", "MediCare Pharmacy", "Healthcare", "8000 Health St, Medical Center, State", "+1-555-1008", "rx@medicare.com"),
        ("MERCHANT_0009", "TravelPro Agency", "Travel", "9000 Journey Ln, Travel Hub, State", "+1-555-1009", "trips@travelpro.com"),
        ("MERCHANT_0010", "CryptoMax Exchange", "Cryptocurrency", "1100 Digital Ave, Crypto Valley, State", "+1-555-1010", "support@cryptomax.com")
    ]
    
    for merchant_data in merchants_data:
        cursor.execute("""
            INSERT OR IGNORE INTO merchants (id, name, category, address, phone, email, risk_score, reputation)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (*merchant_data, random.uniform(0.1, 0.9), random.uniform(0.6, 1.0)))
    
    # Sample transactions
    logger.info("🔄 Generating sample transactions...")
    
    transaction_types = ["purchase", "refund", "transfer", "payment"]
    statuses = ["completed", "pending", "cancelled"]
    
    # Generate 100 sample transactions
    for i in range(100):
        transaction_id = f"TXN_{i+1:04d}"
        user_id = random.choice([u[0] for u in users_data])
        merchant_id = random.choice([m[0] for m in merchants_data])
        amount = round(random.uniform(10.0, 2000.0), 2)
        transaction_type = random.choice(transaction_types)
        status = random.choice(statuses)
        timestamp = datetime.utcnow() - timedelta(days=random.randint(0, 30))
        fraud_score = random.uniform(0.0, 1.0)
        is_flagged = fraud_score > 0.7
        
        cursor.execute("""
            INSERT OR IGNORE INTO transactions 
            (id, user_id, merchant_id, amount, transaction_type, status, timestamp, fraud_score, is_flagged)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (transaction_id, user_id, merchant_id, amount, transaction_type, status, timestamp, fraud_score, is_flagged))
    
    # Create merchant nodes for graph analysis
    logger.info("🕸️ Creating merchant graph nodes...")
    
    for merchant_data in merchants_data:
        merchant_id = merchant_data[0]
        node_id = f"NODE_{merchant_id}"
        
        cursor.execute("""
            INSERT OR IGNORE INTO merchant_nodes 
            (id, merchant_id, centrality_score, clustering_coefficient, pagerank_score, connection_count)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            node_id, merchant_id, 
            random.uniform(0.1, 0.9), 
            random.uniform(0.0, 1.0), 
            random.uniform(0.05, 0.3),
            random.randint(5, 50)
        ))
    
    # Sample flag events for flagged transactions
    logger.info("🚩 Creating flag events...")
    
    cursor.execute("SELECT id FROM transactions WHERE is_flagged = TRUE")
    flagged_transactions = cursor.fetchall()
    
    flag_types = ["anomaly_detection", "risk_threshold", "pattern_match", "manual_review"]
    flag_reasons = [
        "Unusual transaction amount",
        "High-risk merchant",
        "Suspicious timing pattern",
        "Multiple rapid transactions",
        "Geographic anomaly",
        "Behavioral inconsistency"
    ]
    
    for txn in flagged_transactions:
        transaction_id = txn[0]
        flag_id = f"FLAG_{transaction_id}"
        
        cursor.execute("""
            INSERT OR IGNORE INTO flag_events 
            (id, transaction_id, flag_type, flag_reason, confidence_score)
            VALUES (?, ?, ?, ?, ?)
        """, (
            flag_id, transaction_id,
            random.choice(flag_types),
            random.choice(flag_reasons),
            random.uniform(0.7, 0.95)
        ))
    
    conn.commit()
    conn.close()
    
    logger.info("✅ Initial data seeded successfully")

def create_demo_spell_run():
    """Create a demo spell run entry"""
    
    conn = sqlite3.connect("fraudx_copilot.db")
    cursor = conn.cursor()
    
    logger.info("🔮 Creating demo spell run...")
    
    spell_run_data = {
        "id": "SPELL_DEMO_001",
        "spell_type": "rug_pull",
        "parameters": json.dumps({
            "target_merchants": ["MERCHANT_0010"],
            "duration_minutes": 30,
            "impact_multiplier": 2.5
        }),
        "status": "completed",
        "results": json.dumps({
            "success": True,
            "affected_transactions": 45,
            "flagged_transactions": 38,
            "total_impact": 15750.25,
            "detection_rate": 0.84
        }),
        "affected_transactions": 45,
        "flagged_transactions": 38,
        "total_impact": 15750.25,
        "completed_at": datetime.utcnow().isoformat()
    }
    
    cursor.execute("""
        INSERT OR IGNORE INTO spell_runs 
        (id, spell_type, parameters, status, results, affected_transactions, flagged_transactions, total_impact, completed_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        spell_run_data["id"],
        spell_run_data["spell_type"],
        spell_run_data["parameters"],
        spell_run_data["status"],
        spell_run_data["results"],
        spell_run_data["affected_transactions"],
        spell_run_data["flagged_transactions"],
        spell_run_data["total_impact"],
        spell_run_data["completed_at"]
    ))
    
    conn.commit()
    conn.close()
    
    logger.info("✅ Demo spell run created")

def verify_database_setup():
    """Verify that database setup was successful"""
    
    conn = sqlite3.connect("fraudx_copilot.db")
    cursor = conn.cursor()
    
    logger.info("🔍 Verifying database setup...")
    
    # Check table counts
    tables = ["users", "merchants", "transactions", "receipts", "merchant_nodes", "flag_events", "spell_runs"]
    
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        logger.info(f"  📊 {table}: {count} records")
    
    # Check for flagged transactions
    cursor.execute("SELECT COUNT(*) FROM transactions WHERE is_flagged = TRUE")
    flagged_count = cursor.fetchone()[0]
    logger.info(f"  🚨 Flagged transactions: {flagged_count}")
    
    # Check merchant nodes
    cursor.execute("SELECT COUNT(*) FROM merchant_nodes")
    nodes_count = cursor.fetchone()[0]
    logger.info(f"  🕸️ Merchant graph nodes: {nodes_count}")
    
    # Check spell runs
    cursor.execute("SELECT COUNT(*) FROM spell_runs")
    spells_count = cursor.fetchone()[0]
    logger.info(f"  🔮 Spell runs: {spells_count}")
    
    conn.close()
    
    logger.info("✅ Database verification complete")

async def async_main():
    """Main async function for database initialization"""
    logger.info("🚀 Starting FraudX+ Copilot database initialization...")
    
    try:
        # Step 1: Create tables
        create_database_tables()
        
        # Step 2: Seed initial data
        seed_initial_data()
        
        # Step 3: Create demo spell run
        create_demo_spell_run()
        
        # Step 4: Verify setup
        verify_database_setup()
        
        logger.info("🎉 Database initialization completed successfully!")
        logger.info("📍 Database file: fraudx_copilot.db")
        logger.info("🔗 Ready for FastAPI backend connection")
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise

async def init_db():
    """Initialize database for FastAPI"""
    try:
        # Only create tables if they don't exist
        create_database_tables()
        logger.info("✅ Database tables verified/created")
        
        # Check if data exists, if not seed it
        conn = sqlite3.connect("fraudx_copilot.db")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        conn.close()
        
        if user_count == 0:
            seed_initial_data()
            create_demo_spell_run()
            logger.info("✅ Database seeded with initial data")
        else:
            logger.info(f"✅ Database already contains {user_count} users")
            
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        # Don't raise - allow server to start even if DB init fails

def main():
    """Main synchronous entry point"""
    asyncio.run(async_main())

if __name__ == "__main__":
    main()