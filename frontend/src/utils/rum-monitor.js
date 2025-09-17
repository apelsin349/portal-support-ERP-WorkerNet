/**
 * Real User Monitoring (RUM) for frontend performance tracking
 */
class RUMMonitor {
    constructor(apiEndpoint = '/api/metrics/rum') {
        this.apiEndpoint = apiEndpoint;
        this.init();
    }
    
    init() {
        // Core Web Vitals
        this.trackLCP();
        this.trackFID();
        this.trackCLS();
        
        // Custom metrics
        this.trackPageLoad();
        this.trackUserInteractions();
    }
    
    trackLCP() {
        new PerformanceObserver((list) => {
            const entries = list.getEntries();
            const lastEntry = entries[entries.length - 1];
            
            this.sendMetric('lcp', {
                value: lastEntry.startTime,
                url: window.location.href,
                user_agent: navigator.userAgent
            });
        }).observe({ entryTypes: ['largest-contentful-paint'] });
    }
    
    trackFID() {
        new PerformanceObserver((list) => {
            const entries = list.getEntries();
            entries.forEach(entry => {
                this.sendMetric('fid', {
                    value: entry.processingStart - entry.startTime,
                    url: window.location.href
                });
            });
        }).observe({ entryTypes: ['first-input'] });
    }
    
    trackCLS() {
        let clsValue = 0;
        let clsEntries = [];
        
        new PerformanceObserver((list) => {
            for (const entry of list.getEntries()) {
                if (!entry.hadRecentInput) {
                    clsEntries.push(entry);
                    clsValue += entry.value;
                }
            }
            
            this.sendMetric('cls', {
                value: clsValue,
                url: window.location.href
            });
        }).observe({ entryTypes: ['layout-shift'] });
    }
    
    trackPageLoad() {
        window.addEventListener('load', () => {
            const loadTime = performance.timing.loadEventEnd - performance.timing.navigationStart;
            
            this.sendMetric('page_load', {
                value: loadTime,
                url: window.location.href,
                referrer: document.referrer
            });
        });
    }
    
    trackUserInteractions() {
        // Track button clicks
        document.addEventListener('click', (event) => {
            if (event.target.tagName === 'BUTTON' || event.target.closest('button')) {
                this.sendMetric('button_click', {
                    element: event.target.tagName,
                    text: event.target.textContent?.trim(),
                    url: window.location.href
                });
            }
        });
        
        // Track form submissions
        document.addEventListener('submit', (event) => {
            this.sendMetric('form_submit', {
                form_id: event.target.id,
                form_class: event.target.className,
                url: window.location.href
            });
        });
        
        // Track navigation
        window.addEventListener('popstate', () => {
            this.sendMetric('navigation', {
                type: 'popstate',
                url: window.location.href
            });
        });
    }
    
    sendMetric(name, data) {
        const payload = {
            metric: name,
            timestamp: Date.now(),
            session_id: this.getSessionId(),
            user_id: this.getUserId(),
            tenant_id: this.getTenantId(),
            ...data
        };
        
        // Send to backend
        fetch(this.apiEndpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${this.getAuthToken()}`
            },
            body: JSON.stringify(payload)
        }).catch(error => {
            console.warn('Failed to send RUM metric:', error);
        });
    }
    
    getSessionId() {
        let sessionId = sessionStorage.getItem('rum_session_id');
        if (!sessionId) {
            sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
            sessionStorage.setItem('rum_session_id', sessionId);
        }
        return sessionId;
    }
    
    getUserId() {
        // Get from auth context or localStorage
        return localStorage.getItem('user_id') || 'anonymous';
    }
    
    getTenantId() {
        // Get from app context
        return localStorage.getItem('tenant_id') || 'default';
    }
    
    getAuthToken() {
        // Get from auth context
        return localStorage.getItem('auth_token') || '';
    }
}

// Initialize RUM monitoring
const rumMonitor = new RUMMonitor();

// Export for use in other modules
export default rumMonitor;
