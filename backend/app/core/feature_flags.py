"""
Feature Flag System for A/B Testing
"""
from typing import Dict, Any, Optional
import redis
import json
from datetime import datetime


class FeatureFlagManager:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.flags = {}
        self.experiments = {}
    
    def is_enabled(self, flag_name: str, user_id: str, tenant_id: str) -> bool:
        """
        Check if a feature flag is enabled for a user
        
        Args:
            flag_name: Name of the feature flag
            user_id: ID of the user
            tenant_id: ID of the tenant
            
        Returns:
            bool: True if flag is enabled, False otherwise
        """
        flag = self.flags.get(flag_name)
        if not flag:
            return False
        
        # Check if flag is in an active experiment
        experiment = self.experiments.get(flag.experiment_id)
        if experiment and experiment.is_active():
            return self._get_variant(user_id, experiment)
        
        return flag.default_value
    
    def _get_variant(self, user_id: str, experiment: Dict[str, Any]) -> bool:
        """
        Get variant for user in experiment
        
        Args:
            user_id: ID of the user
            experiment: Experiment configuration
            
        Returns:
            bool: True if user should see treatment variant
        """
        # Use consistent hashing to assign users to variants
        user_hash = hash(f"{user_id}_{experiment['id']}") % 100
        
        # Check if user falls within treatment allocation
        treatment_allocation = experiment.get('traffic_allocation', 0.5)
        return user_hash < (treatment_allocation * 100)
    
    def create_experiment(self, experiment_config: Dict[str, Any]) -> str:
        """
        Create a new A/B test experiment
        
        Args:
            experiment_config: Experiment configuration
            
        Returns:
            str: Experiment ID
        """
        experiment_id = f"exp_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        experiment_config['id'] = experiment_id
        experiment_config['status'] = 'draft'
        experiment_config['created_at'] = datetime.utcnow().isoformat()
        
        # Store experiment in Redis
        self.redis.hset(
            f"experiment:{experiment_id}",
            mapping=experiment_config
        )
        
        self.experiments[experiment_id] = experiment_config
        return experiment_id
    
    def start_experiment(self, experiment_id: str) -> bool:
        """
        Start an experiment
        
        Args:
            experiment_id: ID of the experiment
            
        Returns:
            bool: True if started successfully
        """
        experiment = self.experiments.get(experiment_id)
        if not experiment:
            return False
        
        experiment['status'] = 'active'
        experiment['started_at'] = datetime.utcnow().isoformat()
        
        # Update in Redis
        self.redis.hset(
            f"experiment:{experiment_id}",
            mapping=experiment
        )
        
        return True
    
    def stop_experiment(self, experiment_id: str) -> bool:
        """
        Stop an experiment
        
        Args:
            experiment_id: ID of the experiment
            
        Returns:
            bool: True if stopped successfully
        """
        experiment = self.experiments.get(experiment_id)
        if not experiment:
            return False
        
        experiment['status'] = 'stopped'
        experiment['stopped_at'] = datetime.utcnow().isoformat()
        
        # Update in Redis
        self.redis.hset(
            f"experiment:{experiment_id}",
            mapping=experiment
        )
        
        return True
    
    def get_experiment_results(self, experiment_id: str) -> Dict[str, Any]:
        """
        Get experiment results and statistics
        
        Args:
            experiment_id: ID of the experiment
            
        Returns:
            Dict with experiment results
        """
        # This would typically query analytics data
        # For now, return mock data
        return {
            'experiment_id': experiment_id,
            'status': 'active',
            'participants': {
                'control': 1000,
                'treatment': 1000
            },
            'conversions': {
                'control': 150,
                'treatment': 180
            },
            'conversion_rates': {
                'control': 0.15,
                'treatment': 0.18
            },
            'statistical_significance': 0.95,
            'confidence_interval': [0.02, 0.08]
        }
