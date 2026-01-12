"""
Security Module - Input Validation & Rate Limiting
===================================================
Implements OWASP Top-10 protections including:
- Pydantic schema validation with strict types
- IP + user-based rate limiting
- Input sanitization and length limits
- Safe error handling
- Audit logging

All API keys from environment variables only.
"""

import logging
import os
import re
import time
import hashlib
from collections import defaultdict
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Union
from dataclasses import dataclass, field

# Setup logging for audit trail
LOG_DIR = "data/logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Security audit log
audit_handler = logging.FileHandler(os.path.join(LOG_DIR, "security_audit.log"))
audit_handler.setFormatter(logging.Formatter(
    "%(asctime)s - SECURITY - %(levelname)s - %(message)s"
))

audit_logger = logging.getLogger("security.audit")
audit_logger.setLevel(logging.INFO)
audit_logger.addHandler(audit_handler)
audit_logger.addHandler(logging.StreamHandler())


# =============================================================================
# PYDANTIC VALIDATION SCHEMAS
# =============================================================================

try:
    from pydantic import BaseModel, Field, field_validator, ConfigDict
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False
    audit_logger.warning("Pydantic not installed. Using fallback validation.")


if PYDANTIC_AVAILABLE:
    class SearchRequest(BaseModel):
        """Validated search request schema."""
        model_config = ConfigDict(strict=True, extra="forbid")
        
        topic: str = Field(
            ...,
            min_length=3,
            max_length=200,
            description="Research topic to search"
        )
        limit: int = Field(
            default=10,
            ge=1,
            le=20,
            description="Maximum papers to retrieve"
        )
        year_min: Optional[int] = Field(
            default=None,
            ge=1990,
            le=2030,
            description="Minimum publication year"
        )
        min_citations: Optional[int] = Field(
            default=None,
            ge=0,
            le=100000,
            description="Minimum citation count"
        )
        top_n: int = Field(
            default=3,
            ge=1,
            le=10,
            description="Number of top papers to select"
        )
        
        @field_validator("topic")
        @classmethod
        def sanitize_topic(cls, v: str) -> str:
            """Sanitize topic input to prevent injection."""
            # Remove potentially dangerous characters
            sanitized = re.sub(r'[<>"\';\\`${}|]', '', v)
            # Normalize whitespace
            sanitized = ' '.join(sanitized.split())
            return sanitized.strip()
    
    
    class PaperMetadata(BaseModel):
        """Validated paper metadata schema."""
        model_config = ConfigDict(extra="ignore")
        
        paper_id: str = Field(..., max_length=100)
        title: str = Field(..., max_length=500)
        authors: List[str] = Field(default_factory=list, max_length=50)
        abstract: Optional[str] = Field(default=None, max_length=10000)
        year: Optional[int] = Field(default=None, ge=1900, le=2030)
        citation_count: int = Field(default=0, ge=0)
        pdf_url: Optional[str] = Field(default=None, max_length=500)
        pdf_available: bool = Field(default=False)
    
    
    class CritiqueRequest(BaseModel):
        """Validated critique request."""
        model_config = ConfigDict(extra="forbid")
        
        draft_id: Optional[str] = Field(default=None, max_length=100)
        sections: Optional[List[str]] = Field(default=None)
        
        @field_validator("sections")
        @classmethod
        def validate_sections(cls, v):
            if v is None:
                return v
            allowed = {"abstract", "introduction", "methodology_comparison", 
                      "results_synthesis", "conclusion", "references"}
            for section in v:
                if section.lower() not in allowed:
                    raise ValueError(f"Invalid section: {section}")
            return v


# =============================================================================
# RATE LIMITING
# =============================================================================

@dataclass
class RateLimitConfig:
    """Rate limiting configuration."""
    requests_per_minute: int = 30
    requests_per_hour: int = 300
    burst_limit: int = 10
    cooldown_seconds: int = 60


class RateLimiter:
    """
    Token bucket rate limiter with IP and user tracking.
    Implements graceful 429 responses.
    """
    
    def __init__(self, config: RateLimitConfig = None):
        self.config = config or RateLimitConfig()
        self._buckets: Dict[str, List[float]] = defaultdict(list)
        self._cooldowns: Dict[str, float] = {}
    
    def _get_client_id(self, ip: str = None, user_id: str = None) -> str:
        """Generate unique client identifier."""
        identifier = f"{ip or 'unknown'}:{user_id or 'anonymous'}"
        return hashlib.sha256(identifier.encode()).hexdigest()[:16]
    
    def _cleanup_old_requests(self, client_id: str) -> None:
        """Remove requests older than 1 hour."""
        now = time.time()
        hour_ago = now - 3600
        self._buckets[client_id] = [
            ts for ts in self._buckets[client_id] if ts > hour_ago
        ]
    
    def check_rate_limit(self, ip: str = None, user_id: str = None) -> Dict[str, Any]:
        """
        Check if request is allowed under rate limits.
        
        Returns:
            Dict with 'allowed', 'remaining', 'reset_at', 'retry_after'
        """
        client_id = self._get_client_id(ip, user_id)
        now = time.time()
        
        # Check cooldown
        if client_id in self._cooldowns:
            cooldown_end = self._cooldowns[client_id]
            if now < cooldown_end:
                retry_after = int(cooldown_end - now)
                audit_logger.warning(f"Rate limit: Client {client_id} in cooldown for {retry_after}s")
                return {
                    "allowed": False,
                    "reason": "rate_limit_exceeded",
                    "remaining": 0,
                    "reset_at": datetime.fromtimestamp(cooldown_end).isoformat(),
                    "retry_after": retry_after
                }
            else:
                del self._cooldowns[client_id]
        
        self._cleanup_old_requests(client_id)
        requests = self._buckets[client_id]
        
        # Check per-minute limit
        minute_ago = now - 60
        requests_last_minute = len([ts for ts in requests if ts > minute_ago])
        
        if requests_last_minute >= self.config.requests_per_minute:
            self._cooldowns[client_id] = now + self.config.cooldown_seconds
            audit_logger.warning(f"Rate limit exceeded: Client {client_id} - {requests_last_minute}/min")
            return {
                "allowed": False,
                "reason": "minute_limit_exceeded",
                "remaining": 0,
                "reset_at": datetime.fromtimestamp(now + 60).isoformat(),
                "retry_after": 60
            }
        
        # Check per-hour limit
        if len(requests) >= self.config.requests_per_hour:
            audit_logger.warning(f"Rate limit exceeded: Client {client_id} - {len(requests)}/hour")
            return {
                "allowed": False,
                "reason": "hour_limit_exceeded",
                "remaining": 0,
                "reset_at": datetime.fromtimestamp(requests[0] + 3600).isoformat(),
                "retry_after": int(requests[0] + 3600 - now)
            }
        
        # Check burst limit (last 10 seconds)
        ten_seconds_ago = now - 10
        requests_burst = len([ts for ts in requests if ts > ten_seconds_ago])
        
        if requests_burst >= self.config.burst_limit:
            return {
                "allowed": False,
                "reason": "burst_limit_exceeded",
                "remaining": 0,
                "reset_at": datetime.fromtimestamp(now + 10).isoformat(),
                "retry_after": 10
            }
        
        # Request allowed - record it
        self._buckets[client_id].append(now)
        remaining = self.config.requests_per_minute - requests_last_minute - 1
        
        return {
            "allowed": True,
            "remaining": max(0, remaining),
            "reset_at": datetime.fromtimestamp(now + 60).isoformat(),
            "retry_after": 0
        }


# Global rate limiter instance
_rate_limiter = RateLimiter()


def rate_limit(func: Callable) -> Callable:
    """Decorator to apply rate limiting to a function."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Extract IP/user from kwargs if available
        ip = kwargs.pop("client_ip", None)
        user_id = kwargs.pop("user_id", None)
        
        result = _rate_limiter.check_rate_limit(ip=ip, user_id=user_id)
        
        if not result["allowed"]:
            raise RateLimitError(
                f"Rate limit exceeded. Retry after {result['retry_after']} seconds.",
                retry_after=result["retry_after"]
            )
        
        return func(*args, **kwargs)
    
    return wrapper


class RateLimitError(Exception):
    """Exception raised when rate limit is exceeded."""
    
    def __init__(self, message: str, retry_after: int = 60):
        super().__init__(message)
        self.retry_after = retry_after
        self.status_code = 429


# =============================================================================
# INPUT SANITIZATION
# =============================================================================

def sanitize_string(value: str, max_length: int = 1000, allow_html: bool = False) -> str:
    """
    Sanitize string input.
    
    Args:
        value: Input string
        max_length: Maximum allowed length
        allow_html: Whether to allow HTML tags
    
    Returns:
        Sanitized string
    """
    if not isinstance(value, str):
        value = str(value)
    
    # Truncate
    value = value[:max_length]
    
    # Remove null bytes
    value = value.replace('\x00', '')
    
    if not allow_html:
        # Remove HTML/script tags
        value = re.sub(r'<[^>]+>', '', value)
        # Escape special characters
        value = value.replace('&', '&amp;')
        value = value.replace('<', '&lt;')
        value = value.replace('>', '&gt;')
    
    # Remove control characters except newline/tab
    value = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', value)
    
    return value.strip()


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal."""
    # Remove directory separators
    filename = os.path.basename(filename)
    # Remove dangerous characters
    filename = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', filename)
    # Limit length
    return filename[:200]


def validate_search_input(
    topic: str,
    limit: int = 10,
    year_min: int = None,
    min_citations: int = None,
    top_n: int = 3
) -> Dict[str, Any]:
    """
    Validate and sanitize search input.
    
    Returns:
        Dict with validated parameters or raises ValueError
    """
    if PYDANTIC_AVAILABLE:
        try:
            request = SearchRequest(
                topic=topic,
                limit=limit,
                year_min=year_min,
                min_citations=min_citations,
                top_n=top_n
            )
            audit_logger.info(f"Input validated: topic='{request.topic[:50]}...'")
            return request.model_dump()
        except Exception as e:
            audit_logger.warning(f"Validation failed: {str(e)}")
            raise ValueError(f"Invalid input: {str(e)}")
    else:
        # Fallback validation without Pydantic
        if not topic or len(topic) < 3:
            raise ValueError("Topic must be at least 3 characters")
        if len(topic) > 200:
            raise ValueError("Topic must be at most 200 characters")
        
        topic = sanitize_string(topic, max_length=200)
        
        limit = max(1, min(20, int(limit or 10)))
        top_n = max(1, min(10, int(top_n or 3)))
        
        if year_min is not None:
            year_min = max(1990, min(2030, int(year_min)))
        
        if min_citations is not None:
            min_citations = max(0, min(100000, int(min_citations)))
        
        return {
            "topic": topic,
            "limit": limit,
            "year_min": year_min,
            "min_citations": min_citations,
            "top_n": top_n
        }


# =============================================================================
# PROMPT INJECTION DEFENSE
# =============================================================================

INJECTION_PATTERNS = [
    r"ignore\s+previous\s+instructions",
    r"disregard\s+all\s+prior",
    r"system\s*:\s*",
    r"<\s*script",
    r"\{\{.*\}\}",
    r"\$\{.*\}",
    r"exec\s*\(",
    r"eval\s*\(",
    r"__import__",
    r"os\.system",
    r"subprocess",
]


def detect_prompt_injection(text: str) -> bool:
    """
    Detect potential prompt injection attacks.
    
    Returns:
        True if injection detected
    """
    text_lower = text.lower()
    
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            audit_logger.warning(f"Prompt injection detected: pattern='{pattern}'")
            return True
    
    return False


def safe_format(template: str, **kwargs) -> str:
    """
    Safely format a template string without allowing code execution.
    
    Uses simple string replacement instead of format() to prevent
    format string attacks.
    """
    result = template
    for key, value in kwargs.items():
        placeholder = "{" + key + "}"
        safe_value = sanitize_string(str(value))
        result = result.replace(placeholder, safe_value)
    return result


# =============================================================================
# SECRETS HANDLING
# =============================================================================

def get_api_key(key_name: str, required: bool = False) -> Optional[str]:
    """
    Safely retrieve API key from environment variables.
    
    Args:
        key_name: Name of the environment variable
        required: If True, raises error when missing
    
    Returns:
        API key or None
    """
    # NEVER hardcode keys
    value = os.environ.get(key_name)
    
    if required and not value:
        audit_logger.error(f"Required API key missing: {key_name}")
        raise EnvironmentError(f"Required environment variable {key_name} not set")
    
    if value:
        # Log that key was accessed (not the value!)
        audit_logger.info(f"API key accessed: {key_name}")
    
    return value


def mask_sensitive(value: str, visible_chars: int = 4) -> str:
    """Mask a sensitive value for logging."""
    if not value or len(value) <= visible_chars:
        return "****"
    return value[:visible_chars] + "*" * (len(value) - visible_chars)


# =============================================================================
# SAFE ERROR HANDLING
# =============================================================================

class SafeError(Exception):
    """Exception that's safe to show to users (no sensitive data)."""
    
    def __init__(self, message: str, code: str = "UNKNOWN_ERROR", status: int = 500):
        super().__init__(message)
        self.code = code
        self.status = status
        self.timestamp = datetime.now().isoformat()


def handle_error_safely(error: Exception, context: str = "") -> Dict[str, Any]:
    """
    Handle an error safely without exposing sensitive information.
    
    Returns:
        Safe error response dict
    """
    # Log full error for debugging (not exposed to user)
    audit_logger.error(f"Error in {context}: {type(error).__name__}: {str(error)}")
    
    # Determine safe message
    if isinstance(error, SafeError):
        return {
            "error": True,
            "code": error.code,
            "message": str(error),
            "status": error.status
        }
    elif isinstance(error, RateLimitError):
        return {
            "error": True,
            "code": "RATE_LIMIT_EXCEEDED",
            "message": "Too many requests. Please try again later.",
            "status": 429,
            "retry_after": error.retry_after
        }
    elif isinstance(error, ValueError):
        return {
            "error": True,
            "code": "VALIDATION_ERROR",
            "message": "Invalid input provided.",
            "status": 400
        }
    else:
        # Generic error - don't expose details
        return {
            "error": True,
            "code": "INTERNAL_ERROR",
            "message": "An unexpected error occurred. Please try again.",
            "status": 500
        }


# =============================================================================
# AUDIT LOGGING
# =============================================================================

def log_access(action: str, user_id: str = None, ip: str = None, details: Dict = None):
    """Log an access event for audit trail."""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "user_id": user_id or "anonymous",
        "ip": ip or "unknown",
        "details": details or {}
    }
    audit_logger.info(f"ACCESS: {action} by {entry['user_id']} from {entry['ip']}")


def log_security_event(event_type: str, severity: str, details: Dict):
    """Log a security event."""
    audit_logger.warning(f"SECURITY [{severity.upper()}]: {event_type} - {details}")


# =============================================================================
# MIDDLEWARE FOR GRADIO/FLASK
# =============================================================================

def security_middleware(func: Callable) -> Callable:
    """
    Security middleware that wraps request handlers.
    Applies rate limiting, input validation, and error handling.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            # Apply rate limiting
            rate_result = _rate_limiter.check_rate_limit()
            if not rate_result["allowed"]:
                return {
                    "error": True,
                    "message": f"Rate limit exceeded. Retry after {rate_result['retry_after']}s",
                    "retry_after": rate_result["retry_after"]
                }
            
            # Log access
            log_access(func.__name__)
            
            # Execute function
            result = func(*args, **kwargs)
            return result
            
        except Exception as e:
            return handle_error_safely(e, context=func.__name__)
    
    return wrapper


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "SearchRequest",
    "PaperMetadata",
    "CritiqueRequest",
    "RateLimiter",
    "RateLimitError",
    "rate_limit",
    "sanitize_string",
    "sanitize_filename",
    "validate_search_input",
    "detect_prompt_injection",
    "safe_format",
    "get_api_key",
    "mask_sensitive",
    "SafeError",
    "handle_error_safely",
    "log_access",
    "log_security_event",
    "security_middleware"
]
