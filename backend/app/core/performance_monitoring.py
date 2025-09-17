"""
Performance Monitoring and APM
"""
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from opentelemetry import trace
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import redis
import json


@dataclass
class PerformanceMetrics:
    """Performance metrics data structure"""
    response_time: float
    request_count: int
    error_count: int
    active_connections: int
    memory_usage: int
    cpu_usage: float
    timestamp: float


class APMInstrumentation:
    """Application Performance Monitoring instrumentation"""
    
    def __init__(self):
        self.tracer = trace.get_tracer(__name__)
        self.setup_instrumentation()
    
    def setup_instrumentation(self):
        """Setup instrumentation for various components"""
        # Instrument HTTP requests
        RequestsInstrumentor().instrument()
        
        # Instrument database queries
        self.instrument_database()
        
        # Instrument Redis operations
        self.instrument_redis()
    
    def instrument_database(self):
        """Instrument database operations"""
        # This would typically use database-specific instrumentation
        pass
    
    def instrument_redis(self):
        """Instrument Redis operations"""
        # This would typically use Redis-specific instrumentation
        pass
    
    def trace_request(self, operation_name: str):
        """Decorator for tracing requests"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                with self.tracer.start_as_current_span(operation_name) as span:
                    span.set_attribute("service.name", "worker-net-api")
                    span.set_attribute("operation.type", "api_call")
                    
                    start_time = time.time()
                    result = func(*args, **kwargs)
                    duration = time.time() - start_time
                    
                    span.set_attribute("duration", duration)
                    span.set_attribute("status", "success" if result else "error")
                    
                    return result
            return wrapper
        return decorator


class PerformanceCollector:
    """Performance metrics collection"""
    
    def __init__(self):
        self.metrics = {
            'response_time': Histogram(
                'http_request_duration_seconds',
                'HTTP request duration in seconds',
                ['method', 'endpoint', 'status_code']
            ),
            'request_count': Counter(
                'http_requests_total',
                'Total HTTP requests',
                ['method', 'endpoint', 'status_code']
            ),
            'error_count': Counter(
                'http_errors_total',
                'Total HTTP errors',
                ['method', 'endpoint', 'status_code']
            ),
            'active_connections': Gauge(
                'active_connections',
                'Number of active connections'
            ),
            'memory_usage': Gauge(
                'memory_usage_bytes',
                'Memory usage in bytes'
            ),
            'cpu_usage': Gauge(
                'cpu_usage_percent',
                'CPU usage percentage'
            )
        }
    
    def record_request(self, method: str, endpoint: str, 
                      status_code: int, duration: float):
        """
        Record HTTP request metrics
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            status_code: HTTP status code
            duration: Request duration in seconds
        """
        labels = {
            'method': method,
            'endpoint': endpoint,
            'status_code': str(status_code)
        }
        
        self.metrics['response_time'].observe(duration, **labels)
        self.metrics['request_count'].inc(**labels)
        
        if status_code >= 400:
            self.metrics['error_count'].inc(**labels)
    
    def record_system_metrics(self, memory_usage: int, cpu_usage: float):
        """
        Record system metrics
        
        Args:
            memory_usage: Memory usage in bytes
            cpu_usage: CPU usage percentage
        """
        self.metrics['memory_usage'].set(memory_usage)
        self.metrics['cpu_usage'].set(cpu_usage)


class DatabaseMonitor:
    """Database performance monitoring"""
    
    def __init__(self, db_pool):
        self.db_pool = db_pool
        self.metrics = {
            'active_connections': Gauge('db_active_connections', 'Active DB connections'),
            'idle_connections': Gauge('db_idle_connections', 'Idle DB connections'),
            'connection_errors': Counter('db_connection_errors', 'DB connection errors'),
            'query_duration': Histogram(
                'db_query_duration_seconds',
                'Database query duration',
                ['query_type']
            )
        }
    
    def monitor_connections(self):
        """Monitor database connections"""
        stats = self.db_pool.get_stats()
        self.metrics['active_connections'].set(stats['active_connections'])
        self.metrics['idle_connections'].set(stats['idle_connections'])
    
    def track_query(self, query: str, duration: float):
        """
        Track database query performance
        
        Args:
            query: SQL query
            duration: Query duration in seconds
        """
        query_type = self._get_query_type(query)
        self.metrics['query_duration'].observe(duration, query_type=query_type)
    
    def _get_query_type(self, query: str) -> str:
        """Determine query type from SQL"""
        query_upper = query.upper().strip()
        if query_upper.startswith('SELECT'):
            return 'SELECT'
        elif query_upper.startswith('INSERT'):
            return 'INSERT'
        elif query_upper.startswith('UPDATE'):
            return 'UPDATE'
        elif query_upper.startswith('DELETE'):
            return 'DELETE'
        else:
            return 'OTHER'


class RUMMonitor:
    """Real User Monitoring for frontend"""
    
    def __init__(self, api_endpoint: str):
        self.api_endpoint = api_endpoint
        self.metrics = {
            'lcp': Histogram('rum_lcp_seconds', 'Largest Contentful Paint'),
            'fid': Histogram('rum_fid_seconds', 'First Input Delay'),
            'cls': Histogram('rum_cls_score', 'Cumulative Layout Shift'),
            'page_load': Histogram('rum_page_load_seconds', 'Page load time')
        }
    
    def track_lcp(self, value: float, url: str, user_agent: str):
        """Track Largest Contentful Paint"""
        self.metrics['lcp'].observe(value)
        self._send_metric('lcp', {
            'value': value,
            'url': url,
            'user_agent': user_agent
        })
    
    def track_fid(self, value: float, url: str):
        """Track First Input Delay"""
        self.metrics['fid'].observe(value)
        self._send_metric('fid', {
            'value': value,
            'url': url
        })
    
    def track_cls(self, value: float, url: str):
        """Track Cumulative Layout Shift"""
        self.metrics['cls'].observe(value)
        self._send_metric('cls', {
            'value': value,
            'url': url
        })
    
    def track_page_load(self, value: float, url: str):
        """Track page load time"""
        self.metrics['page_load'].observe(value)
        self._send_metric('page_load', {
            'value': value,
            'url': url
        })
    
    def _send_metric(self, name: str, data: Dict[str, Any]):
        """Send metric to backend"""
        # This would typically send to the API endpoint
        pass


class SyntheticMonitor:
    """Synthetic monitoring for automated testing"""
    
    def __init__(self):
        self.test_scenarios = [
            self.test_user_login,
            self.test_ticket_creation,
            self.test_api_endpoints,
            self.test_database_queries
        ]
    
    def run_synthetic_tests(self) -> List[Dict[str, Any]]:
        """
        Run all synthetic tests
        
        Returns:
            List of test results
        """
        results = []
        for scenario in self.test_scenarios:
            result = self.execute_scenario(scenario)
            results.append(result)
        return results
    
    def test_user_login(self) -> Dict[str, Any]:
        """Test user login scenario"""
        start_time = time.time()
        
        # Simulate user login
        # response = requests.post('/api/auth/login', {...})
        # For now, simulate success
        success = True
        status_code = 200
        
        duration = time.time() - start_time
        
        return {
            'scenario': 'user_login',
            'duration': duration,
            'status_code': status_code,
            'success': success
        }
    
    def test_ticket_creation(self) -> Dict[str, Any]:
        """Test ticket creation scenario"""
        start_time = time.time()
        
        # Simulate ticket creation
        success = True
        status_code = 201
        
        duration = time.time() - start_time
        
        return {
            'scenario': 'ticket_creation',
            'duration': duration,
            'status_code': status_code,
            'success': success
        }
    
    def test_api_endpoints(self) -> Dict[str, Any]:
        """Test API endpoints"""
        start_time = time.time()
        
        # Test various API endpoints
        success = True
        status_code = 200
        
        duration = time.time() - start_time
        
        return {
            'scenario': 'api_endpoints',
            'duration': duration,
            'status_code': status_code,
            'success': success
        }
    
    def test_database_queries(self) -> Dict[str, Any]:
        """Test database queries"""
        start_time = time.time()
        
        # Test database performance
        success = True
        status_code = 200
        
        duration = time.time() - start_time
        
        return {
            'scenario': 'database_queries',
            'duration': duration,
            'status_code': status_code,
            'success': success
        }
    
    def execute_scenario(self, scenario_func) -> Dict[str, Any]:
        """Execute a test scenario"""
        try:
            return scenario_func()
        except Exception as e:
            return {
                'scenario': scenario_func.__name__,
                'duration': 0,
                'status_code': 500,
                'success': False,
                'error': str(e)
            }


class CacheManager:
    """Cache management for performance optimization"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.cache_ttl = {
            'user_profile': 3600,  # 1 hour
            'ticket_list': 300,    # 5 minutes
            'knowledge_articles': 1800,  # 30 minutes
            'system_config': 7200  # 2 hours
        }
    
    def get_or_set(self, key: str, fetch_func, ttl: Optional[int] = None) -> Any:
        """
        Get value from cache or set it using fetch function
        
        Args:
            key: Cache key
            fetch_func: Function to fetch data if not in cache
            ttl: Time to live in seconds
            
        Returns:
            Cached or fetched data
        """
        cached = self.redis.get(key)
        if cached:
            return json.loads(cached)
        
        data = fetch_func()
        ttl = ttl or self.cache_ttl.get(key.split(':')[0], 3600)
        self.redis.setex(key, ttl, json.dumps(data))
        return data
    
    def invalidate(self, pattern: str):
        """
        Invalidate cache keys matching pattern
        
        Args:
            pattern: Redis pattern to match
        """
        keys = self.redis.keys(pattern)
        if keys:
            self.redis.delete(*keys)


class QueryOptimizer:
    """Database query optimization"""
    
    def __init__(self, threshold: float = 1000):
        self.threshold = threshold  # milliseconds
    
    def optimize_query(self, query: str, params: Dict[str, Any]) -> str:
        """
        Optimize database query
        
        Args:
            query: SQL query
            params: Query parameters
            
        Returns:
            Optimized query
        """
        # Add query hints
        optimized_query = self.add_hints(query)
        
        # Use prepared statements
        prepared_query = self.prepare_statement(optimized_query)
        
        # Add query plan analysis
        plan = self.analyze_query_plan(prepared_query, params)
        
        if plan['cost'] > self.threshold:
            self.log_slow_query(query, plan)
            return self.suggest_optimization(query, plan)
        
        return prepared_query
    
    def add_hints(self, query: str) -> str:
        """Add query hints for optimization"""
        # This would add database-specific hints
        return query
    
    def prepare_statement(self, query: str) -> str:
        """Prepare statement for execution"""
        # This would prepare the statement
        return query
    
    def analyze_query_plan(self, query: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze query execution plan"""
        # This would analyze the query plan
        return {'cost': 500, 'rows': 1000}
    
    def log_slow_query(self, query: str, plan: Dict[str, Any]):
        """Log slow query for analysis"""
        # This would log to a slow query log
        pass
    
    def suggest_optimization(self, query: str, plan: Dict[str, Any]) -> str:
        """Suggest query optimizations"""
        # This would suggest optimizations
        return query


class PerformanceAlerting:
    """Performance alerting system"""
    
    def __init__(self):
        self.alert_rules = {
            'high_response_time': {
                'threshold': 2.0,  # seconds
                'duration': 300,   # 5 minutes
                'severity': 'warning'
            },
            'high_error_rate': {
                'threshold': 0.05,  # 5%
                'duration': 120,    # 2 minutes
                'severity': 'critical'
            },
            'database_slow_queries': {
                'threshold': 5.0,   # seconds
                'duration': 180,    # 3 minutes
                'severity': 'warning'
            }
        }
    
    def check_alerts(self, metrics: PerformanceMetrics) -> List[Dict[str, Any]]:
        """
        Check if any alerts should be triggered
        
        Args:
            metrics: Current performance metrics
            
        Returns:
            List of triggered alerts
        """
        alerts = []
        
        # Check response time
        if metrics.response_time > self.alert_rules['high_response_time']['threshold']:
            alerts.append({
                'type': 'high_response_time',
                'value': metrics.response_time,
                'threshold': self.alert_rules['high_response_time']['threshold'],
                'severity': 'warning'
            })
        
        # Check error rate
        error_rate = metrics.error_count / max(metrics.request_count, 1)
        if error_rate > self.alert_rules['high_error_rate']['threshold']:
            alerts.append({
                'type': 'high_error_rate',
                'value': error_rate,
                'threshold': self.alert_rules['high_error_rate']['threshold'],
                'severity': 'critical'
            })
        
        return alerts
