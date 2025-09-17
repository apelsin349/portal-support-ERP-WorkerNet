"""
API Versioning System
"""
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import json


class VersioningStrategy(Enum):
    """API versioning strategies"""
    URL = "url"
    HEADER = "header"
    QUERY_PARAM = "query_param"


class APIVersion(Enum):
    """API versions"""
    V1 = "v1"
    V2 = "v2"
    V3 = "v3"
    V4 = "v4"


class VersionStatus(Enum):
    """Version status"""
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    SUNSET = "sunset"
    BETA = "beta"


@dataclass
class VersionInfo:
    """API version information"""
    version: str
    status: VersionStatus
    deprecation_date: Optional[datetime]
    sunset_date: Optional[datetime]
    migration_guide: Optional[str]
    breaking_changes: List[Dict[str, Any]]


class APIVersionRouter:
    """API version routing"""
    
    def __init__(self):
        self.versions = {
            'v1': V1APIHandler(),
            'v2': V2APIHandler(),
            'v3': V3APIHandler()
        }
        self.version_info = self._load_version_info()
    
    def route_request(self, version: str, endpoint: str, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Route request to appropriate version handler
        
        Args:
            version: API version
            endpoint: API endpoint
            request: Request data
            
        Returns:
            Response data
        """
        handler = self.versions.get(version)
        if not handler:
            raise APIVersionNotFound(f"Version {version} not found")
        
        # Check if version is deprecated
        if self._is_deprecated(version):
            self._add_deprecation_warning(version, request)
        
        return handler.handle(endpoint, request)
    
    def _is_deprecated(self, version: str) -> bool:
        """Check if version is deprecated"""
        version_info = self.version_info.get(version)
        if not version_info:
            return False
        
        return version_info.status == VersionStatus.DEPRECATED
    
    def _add_deprecation_warning(self, version: str, request: Dict[str, Any]):
        """Add deprecation warning to response"""
        version_info = self.version_info.get(version)
        if version_info and version_info.migration_guide:
            # Add warning header
            pass
    
    def _load_version_info(self) -> Dict[str, VersionInfo]:
        """Load version information"""
        return {
            'v1': VersionInfo(
                version='v1',
                status=VersionStatus.DEPRECATED,
                deprecation_date=datetime(2024, 1, 1),
                sunset_date=datetime(2025, 1, 1),
                migration_guide='https://docs.workernet.com/migration/v1-to-v2',
                breaking_changes=[
                    {
                        'endpoint': '/api/v1/tickets',
                        'change': "field 'priority' renamed to 'ticket_priority'",
                        'migration': "Use 'ticket_priority' instead of 'priority'"
                    }
                ]
            ),
            'v2': VersionInfo(
                version='v2',
                status=VersionStatus.ACTIVE,
                deprecation_date=None,
                sunset_date=None,
                migration_guide=None,
                breaking_changes=[]
            ),
            'v3': VersionInfo(
                version='v3',
                status=VersionStatus.ACTIVE,
                deprecation_date=None,
                sunset_date=None,
                migration_guide=None,
                breaking_changes=[]
            )
        }


class APIVersionHandler:
    """Base API version handler"""
    
    def handle(self, endpoint: str, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle API request"""
        raise NotImplementedError


class V1APIHandler(APIVersionHandler):
    """V1 API handler"""
    
    def __init__(self):
        self.features = {
            'advanced_search': False,
            'real_time': False,
            'graphql': False
        }
    
    def handle(self, endpoint: str, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle V1 API request"""
        # V1 implementation
        return {
            'version': 'v1',
            'endpoint': endpoint,
            'data': request,
            'features': self.features
        }


class V2APIHandler(APIVersionHandler):
    """V2 API handler"""
    
    def __init__(self):
        self.features = {
            'advanced_search': True,
            'real_time': False,
            'graphql': False
        }
    
    def handle(self, endpoint: str, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle V2 API request"""
        # V2 implementation
        return {
            'version': 'v2',
            'endpoint': endpoint,
            'data': request,
            'features': self.features
        }


class V3APIHandler(APIVersionHandler):
    """V3 API handler"""
    
    def __init__(self):
        self.features = {
            'advanced_search': True,
            'real_time': True,
            'graphql': True
        }
    
    def handle(self, endpoint: str, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle V3 API request"""
        # V3 implementation
        return {
            'version': 'v3',
            'endpoint': endpoint,
            'data': request,
            'features': self.features
        }


class APIVersionManager:
    """API version management"""
    
    def __init__(self):
        self.router = APIVersionRouter()
        self.version_usage = {}
    
    def get_version_info(self, version: str) -> Optional[VersionInfo]:
        """Get version information"""
        return self.router.version_info.get(version)
    
    def get_all_versions(self) -> Dict[str, VersionInfo]:
        """Get all version information"""
        return self.router.version_info
    
    def track_version_usage(self, version: str, endpoint: str):
        """Track version usage for analytics"""
        key = f"{version}:{endpoint}"
        self.version_usage[key] = self.version_usage.get(key, 0) + 1
    
    def get_version_usage_stats(self) -> Dict[str, int]:
        """Get version usage statistics"""
        return self.version_usage
    
    def migrate_request(self, from_version: str, to_version: str, 
                       endpoint: str, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Migrate request from one version to another
        
        Args:
            from_version: Source version
            to_version: Target version
            endpoint: API endpoint
            request: Request data
            
        Returns:
            Migrated request data
        """
        # This would contain migration logic
        # For now, return the request as-is
        return request
    
    def validate_request(self, version: str, endpoint: str, 
                        request: Dict[str, Any]) -> bool:
        """
        Validate request against version schema
        
        Args:
            version: API version
            endpoint: API endpoint
            request: Request data
            
        Returns:
            True if valid, False otherwise
        """
        # This would validate against version-specific schemas
        return True


class APIVersionMiddleware:
    """Middleware for API versioning"""
    
    def __init__(self, version_manager: APIVersionManager):
        self.version_manager = version_manager
    
    def process_request(self, request) -> str:
        """
        Extract API version from request
        
        Args:
            request: HTTP request
            
        Returns:
            API version string
        """
        # Try different versioning strategies
        version = self._extract_from_url(request)
        if version:
            return version
        
        version = self._extract_from_header(request)
        if version:
            return version
        
        version = self._extract_from_query_param(request)
        if version:
            return version
        
        # Default to latest version
        return 'v2'
    
    def _extract_from_url(self, request) -> Optional[str]:
        """Extract version from URL path"""
        path = request.path
        if path.startswith('/api/v'):
            parts = path.split('/')
            if len(parts) >= 3:
                return parts[2]
        return None
    
    def _extract_from_header(self, request) -> Optional[str]:
        """Extract version from header"""
        # Check API-Version header
        version = request.headers.get('API-Version')
        if version:
            return version
        
        # Check Accept header
        accept = request.headers.get('Accept', '')
        if 'application/vnd.workernet.' in accept:
            # Extract version from Accept header
            # e.g., application/vnd.workernet.v2+json
            parts = accept.split('.')
            if len(parts) >= 2:
                version_part = parts[1].split('+')[0]
                return version_part
        
        return None
    
    def _extract_from_query_param(self, request) -> Optional[str]:
        """Extract version from query parameter"""
        return request.args.get('version')


class APIVersionException(Exception):
    """API version related exceptions"""
    pass


class APIVersionNotFound(APIVersionException):
    """Version not found exception"""
    pass


class APIVersionDeprecated(APIVersionException):
    """Version deprecated exception"""
    pass


class APIVersionSunset(APIVersionException):
    """Version sunset exception"""
    pass


# Feature flags per version
VERSION_FEATURES = {
    "v1": {
        "features": {
            "advanced_search": False,
            "real_time": False,
            "graphql": False
        }
    },
    "v2": {
        "features": {
            "advanced_search": True,
            "real_time": False,
            "graphql": False
        }
    },
    "v3": {
        "features": {
            "advanced_search": True,
            "real_time": True,
            "graphql": True
        }
    }
}


def get_version_features(version: str) -> Dict[str, Any]:
    """Get features available for a version"""
    return VERSION_FEATURES.get(version, VERSION_FEATURES["v2"])


def is_feature_enabled(version: str, feature: str) -> bool:
    """Check if a feature is enabled for a version"""
    features = get_version_features(version)
    return features["features"].get(feature, False)
