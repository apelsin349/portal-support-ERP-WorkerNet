/**
 * A/B Testing utilities for frontend
 */
class ABTestingManager {
    constructor() {
        this.experiments = new Map();
        this.userId = this.getUserId();
        this.tenantId = this.getTenantId();
        this.init();
    }
    
    init() {
        // Load active experiments
        this.loadExperiments();
        
        // Track page views
        this.trackPageView();
    }
    
    async loadExperiments() {
        try {
            const response = await fetch('/api/ab-tests/active', {
                headers: {
                    'Authorization': `Bearer ${this.getAuthToken()}`
                }
            });
            
            if (response.ok) {
                const experiments = await response.json();
                experiments.forEach(exp => {
                    this.experiments.set(exp.id, exp);
                });
            }
        } catch (error) {
            console.warn('Failed to load experiments:', error);
        }
    }
    
    isExperimentActive(experimentId) {
        const experiment = this.experiments.get(experimentId);
        return experiment && experiment.status === 'active';
    }
    
    getVariant(experimentId) {
        const experiment = this.experiments.get(experimentId);
        if (!experiment || !this.isExperimentActive(experimentId)) {
            return 'control';
        }
        
        // Use consistent hashing to assign users to variants
        const userHash = this.hash(`${this.userId}_${experimentId}`) % 100;
        const treatmentAllocation = experiment.traffic_allocation || 0.5;
        
        return userHash < (treatmentAllocation * 100) ? 'treatment' : 'control';
    }
    
    getExperimentConfig(experimentId) {
        const experiment = this.experiments.get(experimentId);
        if (!experiment) {
            return null;
        }
        
        const variant = this.getVariant(experimentId);
        const variantConfig = experiment.variants.find(v => v.id === variant);
        
        return {
            experimentId,
            variant,
            config: variantConfig?.config || {},
            experiment: experiment
        };
    }
    
    trackEvent(experimentId, eventName, properties = {}) {
        const experiment = this.experiments.get(experimentId);
        if (!experiment) {
            return;
        }
        
        const variant = this.getVariant(experimentId);
        
        // Send event to analytics
        this.sendEvent({
            experiment_id: experimentId,
            variant: variant,
            event_name: eventName,
            user_id: this.userId,
            tenant_id: this.tenantId,
            timestamp: Date.now(),
            properties: properties
        });
    }
    
    trackConversion(experimentId, conversionType, value = 1) {
        this.trackEvent(experimentId, 'conversion', {
            conversion_type: conversionType,
            value: value
        });
    }
    
    trackPageView(experimentId = null) {
        const experiments = experimentId ? 
            [this.experiments.get(experimentId)].filter(Boolean) :
            Array.from(this.experiments.values());
        
        experiments.forEach(exp => {
            if (this.isExperimentActive(exp.id)) {
                this.trackEvent(exp.id, 'page_view', {
                    url: window.location.href,
                    referrer: document.referrer
                });
            }
        });
    }
    
    applyExperiment(experimentId, callback) {
        const config = this.getExperimentConfig(experimentId);
        if (config) {
            callback(config);
        }
    }
    
    // Feature flag methods
    isFeatureEnabled(featureName, experimentId = null) {
        if (experimentId) {
            const config = this.getExperimentConfig(experimentId);
            return config?.config?.features?.includes(featureName) || false;
        }
        
        // Check all active experiments for this feature
        for (const [expId, experiment] of this.experiments) {
            if (this.isExperimentActive(expId)) {
                const config = this.getExperimentConfig(expId);
                if (config?.config?.features?.includes(featureName)) {
                    return true;
                }
            }
        }
        
        return false;
    }
    
    // Utility methods
    hash(str) {
        let hash = 0;
        for (let i = 0; i < str.length; i++) {
            const char = str.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash; // Convert to 32-bit integer
        }
        return Math.abs(hash);
    }
    
    getUserId() {
        return localStorage.getItem('user_id') || 'anonymous';
    }
    
    getTenantId() {
        return localStorage.getItem('tenant_id') || 'default';
    }
    
    getAuthToken() {
        return localStorage.getItem('auth_token') || '';
    }
    
    async sendEvent(eventData) {
        try {
            await fetch('/api/ab-tests/events', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.getAuthToken()}`
                },
                body: JSON.stringify(eventData)
            });
        } catch (error) {
            console.warn('Failed to send A/B test event:', error);
        }
    }
}

// React hook for A/B testing
export function useABTest(experimentId) {
    const [config, setConfig] = React.useState(null);
    const [loading, setLoading] = React.useState(true);
    
    React.useEffect(() => {
        const abTesting = new ABTestingManager();
        
        const loadConfig = async () => {
            await abTesting.loadExperiments();
            const experimentConfig = abTesting.getExperimentConfig(experimentId);
            setConfig(experimentConfig);
            setLoading(false);
        };
        
        loadConfig();
    }, [experimentId]);
    
    const trackEvent = React.useCallback((eventName, properties) => {
        const abTesting = new ABTestingManager();
        abTesting.trackEvent(experimentId, eventName, properties);
    }, [experimentId]);
    
    const trackConversion = React.useCallback((conversionType, value) => {
        const abTesting = new ABTestingManager();
        abTesting.trackConversion(experimentId, conversionType, value);
    }, [experimentId]);
    
    return {
        config,
        loading,
        trackEvent,
        trackConversion,
        isActive: config?.experiment?.status === 'active',
        variant: config?.variant || 'control'
    };
}

// React component for A/B testing
export function ABTestComponent({ experimentId, children }) {
    const { config, loading } = useABTest(experimentId);
    
    if (loading) {
        return <div>Loading...</div>;
    }
    
    if (!config) {
        return null;
    }
    
    return children(config);
}

// Initialize A/B testing
const abTestingManager = new ABTestingManager();

export default abTestingManager;
