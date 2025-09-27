import networkx as nx
import numpy as np
from typing import Dict, List, Any, Tuple, Optional
import logging
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import json

logger = logging.getLogger(__name__)

class MerchantGraphAnalyzer:
    """
    Graph-based analysis for detecting merchant fraud patterns.
    
    Analyzes:
    - Merchant-customer networks
    - Collusion patterns
    - Centrality and clustering metrics
    - Suspicious transaction flows
    """
    
    def __init__(self):
        self.merchant_graph = nx.Graph()
        self.transaction_graph = nx.DiGraph()  # Directed for transaction flows
        self.risk_cache = {}
        self.cache_ttl = 3600  # 1 hour cache
        
        # Risk thresholds
        self.high_centrality_threshold = 0.8
        self.suspicious_clustering_threshold = 0.9
        self.velocity_threshold = 100  # transactions per hour
        
        logger.info("✅ Merchant Graph Analyzer initialized")
    
    def add_transaction_edge(self, user_id: str, merchant_id: str, amount: float, 
                           timestamp: datetime, metadata: Dict[str, Any] = None):
        """Add transaction as edge to the graph"""
        # Add nodes if they don't exist
        if not self.merchant_graph.has_node(merchant_id):
            self.merchant_graph.add_node(merchant_id, 
                                       node_type='merchant',
                                       total_transactions=0,
                                       total_amount=0.0,
                                       unique_customers=set(),
                                       first_seen=timestamp,
                                       last_seen=timestamp)
        
        if not self.merchant_graph.has_node(user_id):
            self.merchant_graph.add_node(user_id,
                                       node_type='user', 
                                       total_transactions=0,
                                       total_amount=0.0,
                                       unique_merchants=set(),
                                       first_seen=timestamp,
                                       last_seen=timestamp)
        
        # Update node attributes
        merchant_data = self.merchant_graph.nodes[merchant_id]
        user_data = self.merchant_graph.nodes[user_id]
        
        merchant_data['total_transactions'] += 1
        merchant_data['total_amount'] += amount
        merchant_data['unique_customers'].add(user_id)
        merchant_data['last_seen'] = max(merchant_data['last_seen'], timestamp)
        
        user_data['total_transactions'] += 1
        user_data['total_amount'] += amount
        user_data['unique_merchants'].add(merchant_id)
        user_data['last_seen'] = max(user_data['last_seen'], timestamp)
        
        # Add or update edge
        if self.merchant_graph.has_edge(user_id, merchant_id):
            edge_data = self.merchant_graph.edges[user_id, merchant_id]
            edge_data['transaction_count'] += 1
            edge_data['total_amount'] += amount
            edge_data['last_transaction'] = timestamp
            edge_data['amounts'].append(amount)
        else:
            self.merchant_graph.add_edge(user_id, merchant_id,
                                       transaction_count=1,
                                       total_amount=amount,
                                       first_transaction=timestamp,
                                       last_transaction=timestamp,
                                       amounts=[amount])
        
        # Add to directed transaction graph for flow analysis
        self.transaction_graph.add_edge(user_id, merchant_id, 
                                      amount=amount, 
                                      timestamp=timestamp,
                                      metadata=metadata or {})
        
        # Clear relevant cache entries
        self._invalidate_cache(merchant_id, user_id)
    
    def _invalidate_cache(self, merchant_id: str, user_id: str):
        """Invalidate cache entries for affected nodes"""
        keys_to_remove = []
        for key in self.risk_cache:
            if merchant_id in key or user_id in key:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.risk_cache[key]
    
    async def analyze_merchant_risk(self, merchant_id: str, user_id: str = None) -> Dict[str, Any]:
        """
        Analyze risk factors for a merchant in the context of a transaction
        """
        cache_key = f"merchant_risk_{merchant_id}_{user_id or 'none'}"
        
        # Check cache
        if cache_key in self.risk_cache:
            cached_result, timestamp = self.risk_cache[cache_key]
            if (datetime.utcnow() - timestamp).seconds < self.cache_ttl:
                return cached_result
        
        try:
            risk_analysis = {
                "merchant_id": merchant_id,
                "risk_score": 0.0,
                "factors": [],
                "centrality_metrics": {},
                "clustering_metrics": {},
                "velocity_metrics": {},
                "network_anomalies": [],
                "recommendations": []
            }
            
            if not self.merchant_graph.has_node(merchant_id):
                risk_analysis["risk_score"] = 0.1  # Unknown merchant = slight risk
                risk_analysis["factors"].append("Unknown merchant")
                return risk_analysis
            
            # Get merchant data
            merchant_data = self.merchant_graph.nodes[merchant_id]
            
            # 1. Centrality Analysis
            centrality_risk = await self._analyze_centrality(merchant_id)
            risk_analysis["centrality_metrics"] = centrality_risk
            risk_analysis["risk_score"] += centrality_risk["risk_contribution"]
            risk_analysis["factors"].extend(centrality_risk["factors"])
            
            # 2. Clustering Analysis
            clustering_risk = await self._analyze_clustering(merchant_id)
            risk_analysis["clustering_metrics"] = clustering_risk
            risk_analysis["risk_score"] += clustering_risk["risk_contribution"]
            risk_analysis["factors"].extend(clustering_risk["factors"])
            
            # 3. Velocity Analysis
            velocity_risk = await self._analyze_velocity(merchant_id)
            risk_analysis["velocity_metrics"] = velocity_risk
            risk_analysis["risk_score"] += velocity_risk["risk_contribution"]
            risk_analysis["factors"].extend(velocity_risk["factors"])
            
            # 4. Network Anomaly Detection
            anomalies = await self._detect_network_anomalies(merchant_id, user_id)
            risk_analysis["network_anomalies"] = anomalies
            anomaly_risk = len(anomalies) * 0.1
            risk_analysis["risk_score"] += anomaly_risk
            
            # 5. User-Merchant Relationship Analysis (if user provided)
            if user_id:
                relationship_risk = await self._analyze_user_merchant_relationship(user_id, merchant_id)
                risk_analysis["risk_score"] += relationship_risk["risk_contribution"]
                risk_analysis["factors"].extend(relationship_risk["factors"])
            
            # Normalize risk score to [0, 1]
            risk_analysis["risk_score"] = min(1.0, max(0.0, risk_analysis["risk_score"]))
            
            # Generate recommendations
            risk_analysis["recommendations"] = self._generate_recommendations(risk_analysis)
            
            # Cache result
            self.risk_cache[cache_key] = (risk_analysis, datetime.utcnow())
            
            logger.info(f"Merchant {merchant_id} risk analysis: {risk_analysis['risk_score']:.3f}")
            
            return risk_analysis
            
        except Exception as e:
            logger.error(f"❌ Merchant risk analysis failed: {e}")
            return {
                "merchant_id": merchant_id,
                "risk_score": 0.5,  # Default medium risk on error
                "factors": ["Analysis error"],
                "error": str(e)
            }
    
    async def _analyze_centrality(self, merchant_id: str) -> Dict[str, Any]:
        """Analyze merchant centrality in the network"""
        try:
            # Calculate various centrality metrics
            centrality_metrics = {}
            
            if len(self.merchant_graph) > 1:
                # Degree centrality
                degree_centrality = nx.degree_centrality(self.merchant_graph)
                centrality_metrics["degree"] = degree_centrality.get(merchant_id, 0.0)
                
                # Betweenness centrality (computationally expensive for large graphs)
                if len(self.merchant_graph) < 1000:  # Only for smaller graphs
                    betweenness_centrality = nx.betweenness_centrality(self.merchant_graph, k=100)
                    centrality_metrics["betweenness"] = betweenness_centrality.get(merchant_id, 0.0)
                else:
                    centrality_metrics["betweenness"] = 0.0
                
                # Closeness centrality
                if nx.is_connected(self.merchant_graph):
                    closeness_centrality = nx.closeness_centrality(self.merchant_graph)
                    centrality_metrics["closeness"] = closeness_centrality.get(merchant_id, 0.0)
                else:
                    centrality_metrics["closeness"] = 0.0
            else:
                centrality_metrics = {"degree": 0.0, "betweenness": 0.0, "closeness": 0.0}
            
            # Risk assessment
            risk_contribution = 0.0
            factors = []
            
            if centrality_metrics["degree"] > self.high_centrality_threshold:
                risk_contribution += 0.3
                factors.append(f"High degree centrality ({centrality_metrics['degree']:.3f})")
            
            if centrality_metrics["betweenness"] > self.high_centrality_threshold:
                risk_contribution += 0.2
                factors.append(f"High betweenness centrality ({centrality_metrics['betweenness']:.3f})")
            
            return {
                "metrics": centrality_metrics,
                "risk_contribution": risk_contribution,
                "factors": factors
            }
            
        except Exception as e:
            logger.error(f"❌ Centrality analysis failed: {e}")
            return {"metrics": {}, "risk_contribution": 0.0, "factors": []}
    
    async def _analyze_clustering(self, merchant_id: str) -> Dict[str, Any]:
        """Analyze clustering coefficient and community detection"""
        try:
            clustering_metrics = {}
            
            # Local clustering coefficient
            clustering_coeff = nx.clustering(self.merchant_graph, merchant_id)
            clustering_metrics["local_clustering"] = clustering_coeff
            
            # Global clustering coefficient
            clustering_metrics["global_clustering"] = nx.average_clustering(self.merchant_graph)
            
            # Community detection (simplified - use connected components)
            communities = list(nx.connected_components(self.merchant_graph))
            merchant_community_size = 0
            for community in communities:
                if merchant_id in community:
                    merchant_community_size = len(community)
                    break
            
            clustering_metrics["community_size"] = merchant_community_size
            clustering_metrics["total_communities"] = len(communities)
            
            # Risk assessment
            risk_contribution = 0.0
            factors = []
            
            if clustering_coeff > self.suspicious_clustering_threshold:
                risk_contribution += 0.2
                factors.append(f"Suspicious clustering pattern ({clustering_coeff:.3f})")
            
            # Large tightly-knit communities can indicate collusion
            if merchant_community_size > 50 and clustering_coeff > 0.7:
                risk_contribution += 0.3
                factors.append(f"Large tight community ({merchant_community_size} members)")
            
            return {
                "metrics": clustering_metrics,
                "risk_contribution": risk_contribution,
                "factors": factors
            }
            
        except Exception as e:
            logger.error(f"❌ Clustering analysis failed: {e}")
            return {"metrics": {}, "risk_contribution": 0.0, "factors": []}
    
    async def _analyze_velocity(self, merchant_id: str) -> Dict[str, Any]:
        """Analyze transaction velocity patterns"""
        try:
            if not self.merchant_graph.has_node(merchant_id):
                return {"metrics": {}, "risk_contribution": 0.0, "factors": []}
            
            merchant_data = self.merchant_graph.nodes[merchant_id]
            
            # Calculate velocity metrics
            time_span = (merchant_data['last_seen'] - merchant_data['first_seen']).total_seconds() / 3600  # hours
            if time_span == 0:
                time_span = 1  # Avoid division by zero
            
            velocity_metrics = {
                "transactions_per_hour": merchant_data['total_transactions'] / time_span,
                "amount_per_hour": merchant_data['total_amount'] / time_span,
                "unique_customers": len(merchant_data['unique_customers']),
                "avg_transaction_amount": merchant_data['total_amount'] / merchant_data['total_transactions'],
                "time_span_hours": time_span
            }
            
            # Risk assessment
            risk_contribution = 0.0
            factors = []
            
            if velocity_metrics["transactions_per_hour"] > self.velocity_threshold:
                risk_contribution += 0.3
                factors.append(f"High transaction velocity ({velocity_metrics['transactions_per_hour']:.1f}/hour)")
            
            # Very new merchants with high activity
            if time_span < 24 and velocity_metrics["transactions_per_hour"] > 10:
                risk_contribution += 0.2
                factors.append("High activity for new merchant")
            
            # Unusual customer-to-transaction ratio
            cust_txn_ratio = velocity_metrics["unique_customers"] / merchant_data['total_transactions']
            if cust_txn_ratio < 0.1:  # Same customers making many transactions
                risk_contribution += 0.2
                factors.append("Low customer diversity")
            
            return {
                "metrics": velocity_metrics,
                "risk_contribution": risk_contribution,
                "factors": factors
            }
            
        except Exception as e:
            logger.error(f"❌ Velocity analysis failed: {e}")
            return {"metrics": {}, "risk_contribution": 0.0, "factors": []}
    
    async def _detect_network_anomalies(self, merchant_id: str, user_id: str = None) -> List[Dict[str, Any]]:
        """Detect various network anomalies"""
        anomalies = []
        
        try:
            # 1. Detect circular transaction patterns
            if user_id and self._detect_circular_pattern(user_id, merchant_id):
                anomalies.append({
                    "type": "circular_transactions",
                    "description": "Circular transaction pattern detected",
                    "severity": "high"
                })
            
            # 2. Detect burst patterns
            if self._detect_burst_pattern(merchant_id):
                anomalies.append({
                    "type": "transaction_burst",
                    "description": "Unusual transaction burst detected",
                    "severity": "medium"
                })
            
            # 3. Detect merchant chains
            chain_length = self._detect_merchant_chain(merchant_id)
            if chain_length > 5:
                anomalies.append({
                    "type": "merchant_chain",
                    "description": f"Part of {chain_length}-merchant chain",
                    "severity": "medium"
                })
            
            # 4. Detect isolated clusters
            if self._is_isolated_cluster(merchant_id):
                anomalies.append({
                    "type": "isolated_cluster",
                    "description": "Merchant in isolated network cluster",
                    "severity": "low"
                })
            
        except Exception as e:
            logger.error(f"❌ Network anomaly detection failed: {e}")
        
        return anomalies
    
    def _detect_circular_pattern(self, user_id: str, merchant_id: str) -> bool:
        """Detect if user and merchant are part of a circular transaction pattern"""
        try:
            # Look for paths of length 2-4 that connect user back to merchant
            if nx.has_path(self.transaction_graph, merchant_id, user_id):
                shortest_path = nx.shortest_path(self.transaction_graph, merchant_id, user_id)
                return len(shortest_path) <= 5  # Circular if path exists and is short
            return False
        except:
            return False
    
    def _detect_burst_pattern(self, merchant_id: str) -> bool:
        """Detect unusual transaction bursts"""
        # This is a simplified version - in production, analyze time series
        if not self.merchant_graph.has_node(merchant_id):
            return False
        
        merchant_data = self.merchant_graph.nodes[merchant_id]
        time_span_hours = (merchant_data['last_seen'] - merchant_data['first_seen']).total_seconds() / 3600
        
        if time_span_hours < 1 and merchant_data['total_transactions'] > 20:
            return True  # 20+ transactions in under an hour
        
        return False
    
    def _detect_merchant_chain(self, merchant_id: str) -> int:
        """Detect length of merchant chain (connected merchants)"""
        try:
            # Find all merchants connected to this merchant through users
            merchant_neighbors = set()
            for neighbor in self.merchant_graph.neighbors(merchant_id):
                if self.merchant_graph.nodes[neighbor]['node_type'] == 'user':
                    # Find other merchants connected to this user
                    for merchant_neighbor in self.merchant_graph.neighbors(neighbor):
                        if (self.merchant_graph.nodes[merchant_neighbor]['node_type'] == 'merchant' 
                            and merchant_neighbor != merchant_id):
                            merchant_neighbors.add(merchant_neighbor)
            
            return len(merchant_neighbors) + 1  # Include the original merchant
        except:
            return 1
    
    def _is_isolated_cluster(self, merchant_id: str) -> bool:
        """Check if merchant is in an isolated cluster"""
        try:
            # Get the connected component containing this merchant
            component = nx.node_connected_component(self.merchant_graph, merchant_id)
            
            # Check if this component is small and isolated
            if len(component) < 10:  # Small cluster
                # Check if it has very few connections to the main network
                external_connections = 0
                for node in component:
                    for neighbor in self.merchant_graph.neighbors(node):
                        if neighbor not in component:
                            external_connections += 1
                
                return external_connections < 2  # Very few external connections
            
            return False
        except:
            return False
    
    async def _analyze_user_merchant_relationship(self, user_id: str, merchant_id: str) -> Dict[str, Any]:
        """Analyze the specific relationship between user and merchant"""
        if not self.merchant_graph.has_edge(user_id, merchant_id):
            return {"risk_contribution": 0.1, "factors": ["New merchant relationship"]}
        
        edge_data = self.merchant_graph.edges[user_id, merchant_id]
        risk_contribution = 0.0
        factors = []
        
        # Analyze transaction patterns
        transaction_count = edge_data['transaction_count']
        total_amount = edge_data['total_amount']
        avg_amount = total_amount / transaction_count
        
        # High frequency with same merchant
        if transaction_count > 50:
            risk_contribution += 0.2
            factors.append(f"Very frequent transactions ({transaction_count})")
        
        # Unusual amounts
        amounts = edge_data.get('amounts', [])
        if len(amounts) > 1:
            amount_variance = np.var(amounts)
            if amount_variance > avg_amount * 2:  # High variance
                risk_contribution += 0.1
                factors.append("Highly variable transaction amounts")
        
        return {
            "risk_contribution": risk_contribution,
            "factors": factors,
            "relationship_metrics": {
                "transaction_count": transaction_count,
                "total_amount": total_amount,
                "avg_amount": avg_amount,
                "relationship_age_days": (edge_data['last_transaction'] - edge_data['first_transaction']).days
            }
        }
    
    def _generate_recommendations(self, risk_analysis: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations based on risk analysis"""
        recommendations = []
        risk_score = risk_analysis["risk_score"]
        
        if risk_score > 0.8:
            recommendations.append("🚨 IMMEDIATE REVIEW: High-risk merchant requiring urgent investigation")
            recommendations.append("Consider temporary transaction limits")
            recommendations.append("Manual review of recent high-value transactions")
        elif risk_score > 0.6:
            recommendations.append("⚠️ Enhanced monitoring recommended")
            recommendations.append("Review transaction patterns weekly")
            recommendations.append("Consider velocity limits")
        elif risk_score > 0.4:
            recommendations.append("📊 Standard monitoring sufficient")
            recommendations.append("Include in routine risk reports")
        else:
            recommendations.append("✅ Low risk - standard processing")
        
        # Specific recommendations based on factors
        factors = risk_analysis.get("factors", [])
        for factor in factors:
            if "High degree centrality" in factor:
                recommendations.append("Monitor for potential money laundering hub activity")
            elif "High transaction velocity" in factor:
                recommendations.append("Implement velocity-based transaction limits")
            elif "Large tight community" in factor:
                recommendations.append("Investigate potential merchant collusion network")
        
        return recommendations
    
    def get_network_stats(self) -> Dict[str, Any]:
        """Get overall network statistics"""
        stats = {
            "total_nodes": self.merchant_graph.number_of_nodes(),
            "total_edges": self.merchant_graph.number_of_edges(),
            "merchant_nodes": len([n for n, d in self.merchant_graph.nodes(data=True) if d.get('node_type') == 'merchant']),
            "user_nodes": len([n for n, d in self.merchant_graph.nodes(data=True) if d.get('node_type') == 'user']),
            "connected_components": nx.number_connected_components(self.merchant_graph),
            "average_clustering": nx.average_clustering(self.merchant_graph),
            "density": nx.density(self.merchant_graph)
        }
        
        return stats