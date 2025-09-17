"""
A/B Testing Statistical Analysis
"""
import scipy.stats as stats
import numpy as np
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass


@dataclass
class ExperimentResult:
    """Results of an A/B test experiment"""
    control_conversions: int
    control_total: int
    treatment_conversions: int
    treatment_total: int
    confidence_level: float = 0.95
    alpha: float = 0.05


class ABTestAnalyzer:
    """Statistical analysis for A/B tests"""
    
    def __init__(self):
        self.min_sample_size = 1000
        self.confidence_level = 0.95
        self.alpha = 0.05
    
    def calculate_significance(self, control_data: List[float], 
                             treatment_data: List[float], 
                             alpha: float = 0.05) -> Dict[str, Any]:
        """
        Calculate statistical significance for continuous metrics
        
        Args:
            control_data: Control group data
            treatment_data: Treatment group data
            alpha: Significance level
            
        Returns:
            Dict with statistical results
        """
        # T-test for continuous metrics
        t_stat, p_value = stats.ttest_ind(treatment_data, control_data)
        
        # Calculate effect size (Cohen's d)
        effect_size = self._calculate_effect_size(control_data, treatment_data)
        
        return {
            "t_statistic": t_stat,
            "p_value": p_value,
            "significant": p_value < alpha,
            "confidence_level": (1 - alpha) * 100,
            "effect_size": effect_size,
            "practical_significance": abs(effect_size) > 0.2
        }
    
    def calculate_conversion_significance(self, result: ExperimentResult) -> Dict[str, Any]:
        """
        Calculate statistical significance for conversion metrics
        
        Args:
            result: Experiment result data
            
        Returns:
            Dict with conversion analysis results
        """
        # Chi-square test for conversion
        contingency_table = [
            [result.control_conversions, result.control_total - result.control_conversions],
            [result.treatment_conversions, result.treatment_total - result.treatment_conversions]
        ]
        
        chi2_stat, chi2_p_value, dof, expected = stats.chi2_contingency(contingency_table)
        
        # Calculate conversion rates
        control_rate = result.control_conversions / result.control_total
        treatment_rate = result.treatment_conversions / result.treatment_total
        
        # Calculate lift
        lift = (treatment_rate - control_rate) / control_rate if control_rate > 0 else 0
        
        # Calculate confidence interval for lift
        lift_ci = self._calculate_lift_confidence_interval(
            result.control_conversions, result.control_total,
            result.treatment_conversions, result.treatment_total,
            result.confidence_level
        )
        
        return {
            "chi2_statistic": chi2_stat,
            "p_value": chi2_p_value,
            "significant": chi2_p_value < result.alpha,
            "control_rate": control_rate,
            "treatment_rate": treatment_rate,
            "lift": lift,
            "lift_confidence_interval": lift_ci,
            "expected_conversions": expected.tolist()
        }
    
    def calculate_sample_size(self, baseline_rate: float, 
                            minimum_detectable_effect: float, 
                            power: float = 0.8, 
                            alpha: float = 0.05) -> int:
        """
        Calculate required sample size for A/B test
        
        Args:
            baseline_rate: Baseline conversion rate
            minimum_detectable_effect: Minimum detectable effect (as proportion)
            power: Statistical power (1 - beta)
            alpha: Significance level
            
        Returns:
            int: Required sample size per group
        """
        effect_size = minimum_detectable_effect / baseline_rate
        sample_size = stats.power.ttest_power(
            effect_size, 
            alpha=alpha, 
            power=power
        )
        return int(sample_size)
    
    def calculate_power(self, control_data: List[float], 
                       treatment_data: List[float], 
                       alpha: float = 0.05) -> float:
        """
        Calculate statistical power of the test
        
        Args:
            control_data: Control group data
            treatment_data: Treatment group data
            alpha: Significance level
            
        Returns:
            float: Statistical power
        """
        effect_size = self._calculate_effect_size(control_data, treatment_data)
        n = min(len(control_data), len(treatment_data))
        
        power = stats.power.ttest_power(
            effect_size,
            nobs1=n,
            alpha=alpha
        )
        
        return power
    
    def _calculate_effect_size(self, control_data: List[float], 
                             treatment_data: List[float]) -> float:
        """
        Calculate Cohen's d effect size
        
        Args:
            control_data: Control group data
            treatment_data: Treatment group data
            
        Returns:
            float: Effect size
        """
        control_mean = np.mean(control_data)
        treatment_mean = np.mean(treatment_data)
        
        # Pooled standard deviation
        control_std = np.std(control_data, ddof=1)
        treatment_std = np.std(treatment_data, ddof=1)
        
        pooled_std = np.sqrt(
            ((len(control_data) - 1) * control_std**2 + 
             (len(treatment_data) - 1) * treatment_std**2) / 
            (len(control_data) + len(treatment_data) - 2)
        )
        
        if pooled_std == 0:
            return 0
        
        return (treatment_mean - control_mean) / pooled_std
    
    def _calculate_lift_confidence_interval(self, control_conversions: int, 
                                          control_total: int,
                                          treatment_conversions: int, 
                                          treatment_total: int,
                                          confidence_level: float) -> Tuple[float, float]:
        """
        Calculate confidence interval for lift
        
        Args:
            control_conversions: Control group conversions
            control_total: Control group total
            treatment_conversions: Treatment group conversions
            treatment_total: Treatment group total
            confidence_level: Confidence level
            
        Returns:
            Tuple of (lower_bound, upper_bound)
        """
        control_rate = control_conversions / control_total
        treatment_rate = treatment_conversions / treatment_total
        
        # Standard error for difference in proportions
        se = np.sqrt(
            (control_rate * (1 - control_rate) / control_total) +
            (treatment_rate * (1 - treatment_rate) / treatment_total)
        )
        
        # Z-score for confidence level
        z_score = stats.norm.ppf(1 - (1 - confidence_level) / 2)
        
        # Calculate lift
        lift = treatment_rate - control_rate
        
        # Confidence interval
        margin_of_error = z_score * se
        lower_bound = lift - margin_of_error
        upper_bound = lift + margin_of_error
        
        return (lower_bound, upper_bound)
    
    def is_practically_significant(self, result: ExperimentResult, 
                                 min_lift: float = 0.05) -> bool:
        """
        Check if the result is practically significant
        
        Args:
            result: Experiment result
            min_lift: Minimum lift threshold
            
        Returns:
            bool: True if practically significant
        """
        control_rate = result.control_conversions / result.control_total
        treatment_rate = result.treatment_conversions / result.treatment_total
        lift = (treatment_rate - control_rate) / control_rate if control_rate > 0 else 0
        
        return abs(lift) >= min_lift
