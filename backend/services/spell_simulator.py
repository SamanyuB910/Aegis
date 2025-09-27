import numpy as np
import networkx as nx
import random
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime, timedelta
import asyncio

from models.pydantic_schemas import SpellType, SpellContext

logger = logging.getLogger(__name__)

class SpellSimulator:
    """
    Spell simulation engine for testing fraud detection scenarios.
    
    Simulates various attack vectors:
    - Rug Pull: Merchant disappears with funds
    - Oracle Manipulation: Price feed manipulation
    - Sybil Attack: Multiple fake accounts
    - Flash Loan Attack: DeFi protocol exploitation
    - Merchant Collusion: Coordinated fraud network
    """
    
    def __init__(self):
        self.simulation_data = {
            "transactions": [],
            "merchants": {},
            "users": {},
            "network_graph": nx.Graph()
        }
        
        # Spell execution configurations
        self.spell_configs = {
            "rug_pull": {
                "duration_range": (300, 600),  # 5-10 minutes
                "complexity": "medium",
                "impact_multiplier": 2.5
            },
            "oracle_manipulation": {
                "duration_range": (600, 900),  # 10-15 minutes
                "complexity": "high",
                "impact_multiplier": 3.0
            },
            "sybil_attack": {
                "duration_range": (900, 1200),  # 15-20 minutes
                "complexity": "high",
                "impact_multiplier": 2.0
            },
            "flash_loan_attack": {
                "duration_range": (180, 300),  # 3-5 minutes
                "complexity": "critical",
                "impact_multiplier": 4.0
            },
            "merchant_collusion": {
                "duration_range": (1200, 1800),  # 20-30 minutes
                "complexity": "high",
                "impact_multiplier": 3.5
            }
        }
        
        logger.info("✅ Spell Simulator initialized")
    
    async def execute_spell(self, spell_type: SpellType, context: SpellContext, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a fraud simulation spell"""
        try:
            logger.info(f"🔮 Executing spell: {spell_type.value}")
            
            # Get spell configuration
            config = self.spell_configs.get(spell_type.value, {})
            
            # Initialize simulation environment
            await self._setup_simulation_environment(context, parameters)
            
            # Execute specific spell
            if spell_type == SpellType.RUG_PULL:
                result = await self._simulate_rug_pull(context, parameters, config)
            elif spell_type == SpellType.ORACLE_MANIPULATION:
                result = await self._simulate_oracle_manipulation(context, parameters, config)
            elif spell_type == SpellType.SYBIL_ATTACK:
                result = await self._simulate_sybil_attack(context, parameters, config)
            elif spell_type == SpellType.FLASH_LOAN_ATTACK:
                result = await self._simulate_flash_loan_attack(context, parameters, config)
            elif spell_type == SpellType.MERCHANT_COLLUSION:
                result = await self._simulate_merchant_collusion(context, parameters, config)
            else:
                raise ValueError(f"Unknown spell type: {spell_type.value}")
            
            logger.info(f"✅ Spell completed: {spell_type.value}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Spell execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "affected_transactions": 0,
                "flagged_transactions": 0,
                "total_impact": 0.0
            }
    
    async def _setup_simulation_environment(self, context: SpellContext, parameters: Dict[str, Any]):
        """Setup simulation environment with synthetic data"""
        # Generate synthetic merchants
        merchant_count = parameters.get("merchant_count", 10)
        if context.target_merchants:
            merchants = context.target_merchants[:merchant_count]
        else:
            merchants = [f"MERCHANT_{i:04d}" for i in range(merchant_count)]
        
        # Generate synthetic users
        user_count = parameters.get("user_count", 50)
        if context.target_users:
            users = context.target_users[:user_count]
        else:
            users = [f"USER_{i:04d}" for i in range(user_count)]
        
        # Create network graph
        self.simulation_data["network_graph"] = nx.Graph()
        
        # Add merchants and users as nodes
        for merchant in merchants:
            self.simulation_data["merchants"][merchant] = {
                "transaction_count": random.randint(10, 100),
                "total_volume": random.uniform(1000, 50000),
                "risk_score": random.uniform(0.1, 0.9),
                "reputation": random.uniform(0.5, 1.0)
            }
            self.simulation_data["network_graph"].add_node(merchant, node_type="merchant")
        
        for user in users:
            self.simulation_data["users"][user] = {
                "transaction_count": random.randint(5, 50),
                "total_spent": random.uniform(500, 10000),
                "risk_profile": random.choice(["low", "medium", "high"]),
                "account_age": random.randint(30, 1000)
            }
            self.simulation_data["network_graph"].add_node(user, node_type="user")
        
        # Create edges between users and merchants
        for user in users:
            connected_merchants = random.sample(merchants, random.randint(1, min(5, len(merchants))))
            for merchant in connected_merchants:
                transaction_count = random.randint(1, 10)
                total_amount = random.uniform(50, 1000) * transaction_count
                self.simulation_data["network_graph"].add_edge(
                    user, merchant,
                    transaction_count=transaction_count,
                    total_amount=total_amount
                )
    
    async def _simulate_rug_pull(self, context: SpellContext, parameters: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate a rug pull attack where merchants disappear with funds"""
        
        # Select target merchants for rug pull
        target_merchants = list(self.simulation_data["merchants"].keys())[:3]  # Target 3 merchants
        
        affected_transactions = 0
        flagged_transactions = 0
        total_impact = 0.0
        
        attack_timeline = []
        
        # Phase 1: Build reputation (first 30% of time)
        reputation_building_transactions = random.randint(50, 100)
        for _ in range(reputation_building_transactions):
            merchant = random.choice(target_merchants)
            user = random.choice(list(self.simulation_data["users"].keys()))
            amount = random.uniform(10, 100)  # Small amounts to build trust
            
            transaction = {
                "merchant": merchant,
                "user": user,
                "amount": amount,
                "timestamp": datetime.utcnow() - timedelta(hours=random.randint(1, 72)),
                "phase": "reputation_building",
                "fraud_score": random.uniform(0.1, 0.3)  # Low fraud scores initially
            }
            
            self.simulation_data["transactions"].append(transaction)
            affected_transactions += 1
            total_impact += amount
        
        # Phase 2: Escalation (middle 40% of time)
        escalation_transactions = random.randint(30, 60)
        for _ in range(escalation_transactions):
            merchant = random.choice(target_merchants)
            user = random.choice(list(self.simulation_data["users"].keys()))
            amount = random.uniform(100, 500)  # Increasing amounts
            
            # Fraud scores start increasing
            fraud_score = random.uniform(0.3, 0.6)
            
            transaction = {
                "merchant": merchant,
                "user": user,
                "amount": amount,
                "timestamp": datetime.utcnow() - timedelta(hours=random.randint(0, 24)),
                "phase": "escalation",
                "fraud_score": fraud_score
            }
            
            self.simulation_data["transactions"].append(transaction)
            affected_transactions += 1
            total_impact += amount
            
            if fraud_score > 0.5:
                flagged_transactions += 1
        
        # Phase 3: Rug pull execution (final 30% of time)
        rug_pull_transactions = random.randint(20, 40)
        for _ in range(rug_pull_transactions):
            merchant = random.choice(target_merchants)
            user = random.choice(list(self.simulation_data["users"].keys()))
            amount = random.uniform(500, 2000)  # Large amounts during rug pull
            
            # High fraud scores during rug pull
            fraud_score = random.uniform(0.7, 0.95)
            
            transaction = {
                "merchant": merchant,
                "user": user,
                "amount": amount,
                "timestamp": datetime.utcnow() - timedelta(minutes=random.randint(0, 60)),
                "phase": "rug_pull",
                "fraud_score": fraud_score
            }
            
            self.simulation_data["transactions"].append(transaction)
            affected_transactions += 1
            total_impact += amount
            flagged_transactions += 1
            
            attack_timeline.append({
                "timestamp": transaction["timestamp"].isoformat(),
                "event": "large_withdrawal",
                "merchant": merchant,
                "amount": amount,
                "fraud_score": fraud_score
            })
        
        # Simulate short delay for realism
        await asyncio.sleep(2)
        
        return {
            "success": True,
            "spell_type": "rug_pull",
            "affected_transactions": affected_transactions,
            "flagged_transactions": flagged_transactions,
            "total_impact": round(total_impact, 2),
            "target_merchants": target_merchants,
            "attack_phases": ["reputation_building", "escalation", "rug_pull"],
            "timeline": attack_timeline,
            "detection_metrics": {
                "early_detection_rate": flagged_transactions / affected_transactions if affected_transactions > 0 else 0,
                "false_positive_rate": random.uniform(0.05, 0.15),
                "average_fraud_score": sum(t["fraud_score"] for t in self.simulation_data["transactions"]) / len(self.simulation_data["transactions"])
            }
        }
    
    async def _simulate_oracle_manipulation(self, context: SpellContext, parameters: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate oracle price manipulation attack"""
        
        affected_transactions = 0
        flagged_transactions = 0
        total_impact = 0.0
        
        price_manipulations = []
        
        # Simulate price feed manipulation events
        manipulation_events = random.randint(5, 15)
        
        for i in range(manipulation_events):
            # Select random asset
            asset = random.choice(["ETH", "BTC", "USDC", "DAI", "LINK"])
            
            # Generate price manipulation
            normal_price = random.uniform(100, 2000)
            manipulated_price = normal_price * random.uniform(0.7, 1.4)  # ±30% manipulation
            manipulation_duration = random.randint(5, 30)  # minutes
            
            price_manipulation = {
                "asset": asset,
                "normal_price": normal_price,
                "manipulated_price": manipulated_price,
                "manipulation_factor": manipulated_price / normal_price,
                "duration_minutes": manipulation_duration,
                "timestamp": datetime.utcnow() - timedelta(minutes=random.randint(0, 120))
            }
            
            price_manipulations.append(price_manipulation)
            
            # Generate transactions affected by price manipulation
            affected_txn_count = random.randint(10, 30)
            
            for _ in range(affected_txn_count):
                merchant = random.choice(list(self.simulation_data["merchants"].keys()))
                user = random.choice(list(self.simulation_data["users"].keys()))
                
                # Transaction amount affected by manipulated price
                base_amount = random.uniform(50, 500)
                manipulated_amount = base_amount * price_manipulation["manipulation_factor"]
                
                # Higher fraud score for transactions during manipulation
                fraud_score = random.uniform(0.6, 0.9)
                
                transaction = {
                    "merchant": merchant,
                    "user": user,
                    "amount": manipulated_amount,
                    "base_amount": base_amount,
                    "asset": asset,
                    "price_manipulation": price_manipulation,
                    "timestamp": price_manipulation["timestamp"] + timedelta(minutes=random.randint(0, manipulation_duration)),
                    "fraud_score": fraud_score
                }
                
                self.simulation_data["transactions"].append(transaction)
                affected_transactions += 1
                total_impact += abs(manipulated_amount - base_amount)
                
                if fraud_score > 0.7:
                    flagged_transactions += 1
        
        await asyncio.sleep(3)  # Longer simulation for oracle attacks
        
        return {
            "success": True,
            "spell_type": "oracle_manipulation",
            "affected_transactions": affected_transactions,
            "flagged_transactions": flagged_transactions,
            "total_impact": round(total_impact, 2),
            "manipulation_events": len(price_manipulations),
            "price_manipulations": price_manipulations,
            "affected_assets": list(set(pm["asset"] for pm in price_manipulations)),
            "detection_metrics": {
                "manipulation_detection_rate": flagged_transactions / affected_transactions if affected_transactions > 0 else 0,
                "average_price_deviation": sum(abs(pm["manipulation_factor"] - 1.0) for pm in price_manipulations) / len(price_manipulations) if price_manipulations else 0
            }
        }
    
    async def _simulate_sybil_attack(self, context: SpellContext, parameters: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate Sybil attack with multiple fake accounts"""
        
        # Create fake accounts
        fake_account_count = random.randint(20, 50)
        fake_accounts = [f"SYBIL_{i:04d}" for i in range(fake_account_count)]
        
        # Target merchants for the attack
        target_merchants = random.sample(list(self.simulation_data["merchants"].keys()), min(3, len(self.simulation_data["merchants"])))
        
        affected_transactions = 0
        flagged_transactions = 0
        total_impact = 0.0
        
        # Phase 1: Account creation and initial activity
        for fake_account in fake_accounts:
            self.simulation_data["users"][fake_account] = {
                "transaction_count": 0,
                "total_spent": 0,
                "risk_profile": "high",
                "account_age": random.randint(1, 7),  # Very new accounts
                "is_sybil": True
            }
            
            # Each fake account makes transactions with target merchants
            transactions_per_account = random.randint(5, 15)
            
            for _ in range(transactions_per_account):
                merchant = random.choice(target_merchants)
                amount = random.uniform(10, 200)
                
                # Sybil accounts have coordinated behavior patterns
                fraud_score = random.uniform(0.5, 0.8)
                
                transaction = {
                    "merchant": merchant,
                    "user": fake_account,
                    "amount": amount,
                    "timestamp": datetime.utcnow() - timedelta(hours=random.randint(0, 48)),
                    "fraud_score": fraud_score,
                    "attack_type": "sybil",
                    "coordination_pattern": True
                }
                
                self.simulation_data["transactions"].append(transaction)
                affected_transactions += 1
                total_impact += amount
                
                if fraud_score > 0.6:
                    flagged_transactions += 1
        
        # Phase 2: Coordinated attack
        coordination_events = random.randint(3, 8)
        
        for event in range(coordination_events):
            # Select subset of Sybil accounts for coordinated action
            coordinating_accounts = random.sample(fake_accounts, random.randint(5, 15))
            target_merchant = random.choice(target_merchants)
            
            # Coordinated transactions within short time window
            event_timestamp = datetime.utcnow() - timedelta(minutes=random.randint(0, 240))
            
            for account in coordinating_accounts:
                amount = random.uniform(100, 500)
                fraud_score = random.uniform(0.7, 0.95)  # High fraud score for coordinated actions
                
                transaction = {
                    "merchant": target_merchant,
                    "user": account,
                    "amount": amount,
                    "timestamp": event_timestamp + timedelta(seconds=random.randint(0, 300)),  # Within 5-minute window
                    "fraud_score": fraud_score,
                    "attack_type": "sybil_coordination",
                    "coordination_event": event
                }
                
                self.simulation_data["transactions"].append(transaction)
                affected_transactions += 1
                total_impact += amount
                flagged_transactions += 1
        
        await asyncio.sleep(4)  # Longer simulation for Sybil attacks
        
        # Analyze coordination patterns
        coordination_analysis = self._analyze_sybil_coordination(fake_accounts)
        
        return {
            "success": True,
            "spell_type": "sybil_attack",
            "affected_transactions": affected_transactions,
            "flagged_transactions": flagged_transactions,
            "total_impact": round(total_impact, 2),
            "fake_accounts_created": fake_account_count,
            "target_merchants": target_merchants,
            "coordination_events": coordination_events,
            "coordination_analysis": coordination_analysis,
            "detection_metrics": {
                "sybil_detection_rate": flagged_transactions / affected_transactions if affected_transactions > 0 else 0,
                "account_clustering_score": random.uniform(0.7, 0.95),
                "behavioral_similarity": random.uniform(0.8, 0.98)
            }
        }
    
    async def _simulate_flash_loan_attack(self, context: SpellContext, parameters: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate flash loan attack"""
        
        affected_transactions = 0
        flagged_transactions = 0
        total_impact = 0.0
        
        # Flash loan events
        flash_loan_events = random.randint(3, 8)
        attack_events = []
        
        for event_id in range(flash_loan_events):
            # Flash loan parameters
            loan_amount = random.uniform(100000, 1000000)  # Large loan amounts
            exploit_merchant = random.choice(list(self.simulation_data["merchants"].keys()))
            attacker_id = f"FLASHLOAN_ATTACKER_{event_id}"
            
            # Event timeline
            event_start = datetime.utcnow() - timedelta(minutes=random.randint(0, 120))
            
            # Step 1: Take flash loan
            flash_loan_txn = {
                "type": "flash_loan_borrow",
                "amount": loan_amount,
                "user": attacker_id,
                "timestamp": event_start,
                "fraud_score": 0.95,  # Very high fraud score
                "loan_duration_seconds": random.randint(10, 300)
            }
            
            # Step 2: Exploit vulnerability
            exploit_transactions = random.randint(5, 15)
            exploit_profit = 0
            
            for _ in range(exploit_transactions):
                exploit_amount = random.uniform(1000, 10000)
                exploit_profit += exploit_amount * random.uniform(0.05, 0.15)  # 5-15% profit per transaction
                
                exploit_txn = {
                    "type": "exploit_transaction",
                    "merchant": exploit_merchant,
                    "user": attacker_id,
                    "amount": exploit_amount,
                    "timestamp": event_start + timedelta(seconds=random.randint(10, 200)),
                    "fraud_score": random.uniform(0.85, 0.98),
                    "flash_loan_event": event_id
                }
                
                self.simulation_data["transactions"].append(exploit_txn)
                affected_transactions += 1
                flagged_transactions += 1
                total_impact += exploit_amount
            
            # Step 3: Repay flash loan with profit
            repay_txn = {
                "type": "flash_loan_repay",
                "amount": loan_amount,
                "profit": exploit_profit,
                "user": attacker_id,
                "timestamp": event_start + timedelta(seconds=random.randint(200, 300)),
                "fraud_score": 0.9
            }
            
            attack_event = {
                "event_id": event_id,
                "loan_amount": loan_amount,
                "exploit_profit": exploit_profit,
                "exploit_merchant": exploit_merchant,
                "transaction_count": exploit_transactions,
                "duration_seconds": (repay_txn["timestamp"] - event_start).total_seconds(),
                "profitability": exploit_profit / loan_amount,
                "timeline": [flash_loan_txn, repay_txn]
            }
            
            attack_events.append(attack_event)
        
        await asyncio.sleep(1)  # Quick simulation for flash loans
        
        return {
            "success": True,
            "spell_type": "flash_loan_attack",
            "affected_transactions": affected_transactions,
            "flagged_transactions": flagged_transactions,
            "total_impact": round(total_impact, 2),
            "flash_loan_events": flash_loan_events,
            "attack_events": attack_events,
            "total_profit": sum(event["exploit_profit"] for event in attack_events),
            "average_profitability": sum(event["profitability"] for event in attack_events) / len(attack_events) if attack_events else 0,
            "detection_metrics": {
                "flash_loan_detection_rate": 1.0,  # Should be 100% detectable
                "average_attack_duration": sum(event["duration_seconds"] for event in attack_events) / len(attack_events) if attack_events else 0
            }
        }
    
    async def _simulate_merchant_collusion(self, context: SpellContext, parameters: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate merchant collusion network"""
        
        # Create collusion network
        colluding_merchants = random.sample(list(self.simulation_data["merchants"].keys()), min(5, len(self.simulation_data["merchants"])))
        
        affected_transactions = 0
        flagged_transactions = 0
        total_impact = 0.0
        
        # Create shared customers for collusion
        shared_customers = [f"SHARED_CUSTOMER_{i:03d}" for i in range(20)]
        
        for customer in shared_customers:
            self.simulation_data["users"][customer] = {
                "transaction_count": 0,
                "total_spent": 0,
                "risk_profile": "medium",
                "account_age": random.randint(30, 365),
                "is_colluding": True
            }
        
        # Pattern 1: Round-robin transactions
        round_robin_rounds = random.randint(5, 10)
        
        for round_num in range(round_robin_rounds):
            for i, merchant in enumerate(colluding_merchants):
                customer = shared_customers[i % len(shared_customers)]
                amount = random.uniform(200, 800)
                
                # Collusion patterns have moderate fraud scores
                fraud_score = random.uniform(0.4, 0.7)
                
                transaction = {
                    "merchant": merchant,
                    "user": customer,
                    "amount": amount,
                    "timestamp": datetime.utcnow() - timedelta(hours=random.randint(0, 168)),  # Within past week
                    "fraud_score": fraud_score,
                    "pattern": "round_robin",
                    "round": round_num
                }
                
                self.simulation_data["transactions"].append(transaction)
                affected_transactions += 1
                total_impact += amount
                
                if fraud_score > 0.6:
                    flagged_transactions += 1
        
        # Pattern 2: Circular money flow
        circular_flows = random.randint(3, 6)
        
        for flow_id in range(circular_flows):
            flow_amount = random.uniform(1000, 5000)
            
            # Money flows in a circle through merchants
            for i in range(len(colluding_merchants)):
                from_merchant = colluding_merchants[i]
                to_merchant = colluding_merchants[(i + 1) % len(colluding_merchants)]
                
                # Use intermediary customer
                intermediary = random.choice(shared_customers)
                
                # Transaction from merchant A to customer
                txn1 = {
                    "merchant": from_merchant,
                    "user": intermediary,
                    "amount": flow_amount,
                    "timestamp": datetime.utcnow() - timedelta(hours=random.randint(0, 24)),
                    "fraud_score": random.uniform(0.5, 0.8),
                    "pattern": "circular_flow",
                    "flow_id": flow_id,
                    "step": "withdraw"
                }
                
                # Transaction from customer to merchant B
                txn2 = {
                    "merchant": to_merchant,
                    "user": intermediary,
                    "amount": flow_amount * 0.95,  # 5% fee
                    "timestamp": txn1["timestamp"] + timedelta(minutes=random.randint(5, 60)),
                    "fraud_score": random.uniform(0.6, 0.9),
                    "pattern": "circular_flow",
                    "flow_id": flow_id,
                    "step": "deposit"
                }
                
                self.simulation_data["transactions"].extend([txn1, txn2])
                affected_transactions += 2
                total_impact += flow_amount
                
                if txn1["fraud_score"] > 0.6:
                    flagged_transactions += 1
                if txn2["fraud_score"] > 0.6:
                    flagged_transactions += 1
        
        await asyncio.sleep(5)  # Longer simulation for collusion networks
        
        # Analyze collusion network
        network_analysis = self._analyze_collusion_network(colluding_merchants, shared_customers)
        
        return {
            "success": True,
            "spell_type": "merchant_collusion",
            "affected_transactions": affected_transactions,
            "flagged_transactions": flagged_transactions,
            "total_impact": round(total_impact, 2),
            "colluding_merchants": colluding_merchants,
            "shared_customers": len(shared_customers),
            "collusion_patterns": ["round_robin", "circular_flow"],
            "network_analysis": network_analysis,
            "detection_metrics": {
                "collusion_detection_rate": flagged_transactions / affected_transactions if affected_transactions > 0 else 0,
                "network_density": network_analysis.get("density", 0),
                "clustering_coefficient": network_analysis.get("clustering", 0)
            }
        }
    
    def _analyze_sybil_coordination(self, fake_accounts: List[str]) -> Dict[str, Any]:
        """Analyze coordination patterns in Sybil attack"""
        
        # Get transactions from fake accounts
        sybil_transactions = [
            txn for txn in self.simulation_data["transactions"]
            if txn["user"] in fake_accounts
        ]
        
        # Analyze timing patterns
        timestamps = [txn["timestamp"] for txn in sybil_transactions]
        if len(timestamps) > 1:
            time_diffs = [(timestamps[i+1] - timestamps[i]).total_seconds() for i in range(len(timestamps)-1)]
            avg_time_diff = sum(time_diffs) / len(time_diffs)
        else:
            avg_time_diff = 0
        
        # Analyze amount patterns
        amounts = [txn["amount"] for txn in sybil_transactions]
        amount_variance = np.var(amounts) if amounts else 0
        
        return {
            "total_sybil_transactions": len(sybil_transactions),
            "average_time_between_transactions": avg_time_diff,
            "amount_variance": float(amount_variance),
            "coordination_score": random.uniform(0.7, 0.95),
            "behavioral_similarity": random.uniform(0.8, 0.98)
        }
    
    def _analyze_collusion_network(self, merchants: List[str], customers: List[str]) -> Dict[str, Any]:
        """Analyze collusion network structure"""
        
        # Create subgraph with colluding entities
        collusion_graph = nx.Graph()
        
        for merchant in merchants:
            collusion_graph.add_node(merchant, node_type="merchant")
        
        for customer in customers:
            collusion_graph.add_node(customer, node_type="customer")
        
        # Add edges based on transactions
        collusion_transactions = [
            txn for txn in self.simulation_data["transactions"]
            if txn["merchant"] in merchants and txn["user"] in customers
        ]
        
        for txn in collusion_transactions:
            if collusion_graph.has_edge(txn["user"], txn["merchant"]):
                collusion_graph[txn["user"]][txn["merchant"]]["weight"] += 1
            else:
                collusion_graph.add_edge(txn["user"], txn["merchant"], weight=1)
        
        # Calculate network metrics
        density = nx.density(collusion_graph)
        clustering = nx.average_clustering(collusion_graph)
        
        return {
            "nodes": collusion_graph.number_of_nodes(),
            "edges": collusion_graph.number_of_edges(),
            "density": density,
            "clustering": clustering,
            "merchant_count": len(merchants),
            "customer_count": len(customers),
            "transaction_count": len(collusion_transactions)
        }