from typing import List, Dict, Union, Optional
import os
import re
from dataclasses import dataclass
from flask import Flask
from urllib.parse import urlparse

@dataclass
class ConfigError:
    key: str
    message: str
    severity: str = "error"  # error, warning, info

def validate_config(app: Flask) -> List[ConfigError]:
    """Validate both environment and application configuration."""
    errors = []
    
    # Required environment variables with validation rules
    required_vars = {
        'DATABASE_URL': {
            'message': 'Database connection string is required',
            'validator': lambda x: validate_url(x, 'postgresql'),
            'severity': 'error'
        },
        'JWT_SECRET_KEY': {
            'message': 'JWT secret key is required',
            'validator': lambda x: len(x) >= 32,
            'severity': 'error'
        },
        'REDIS_URL': {
            'message': 'Redis connection string is required',
            'validator': lambda x: validate_url(x, 'redis'),
            'severity': 'error'
        },
        'MAIL_SERVER': {
            'message': 'Mail server configuration is required',
            'validator': lambda x: bool(x),
            'severity': 'error'
        },
        'MAIL_PORT': {
            'message': 'Mail port configuration is required',
            'validator': lambda x: int(x) in [25, 465, 587, 2525],
            'severity': 'error'
        },
        'MAIL_USERNAME': {
            'message': 'Mail username is required',
            'validator': lambda x: bool(re.match(r'^[^@]+@[^@]+\.[^@]+$', x)),
            'severity': 'error'
        },
        'MAIL_PASSWORD': {
            'message': 'Mail password is required',
            'validator': lambda x: len(x) >= 8,
            'severity': 'error'
        }
    }

    # Validate configuration
    for key, rules in required_vars.items():
        value = app.config.get(key) or os.getenv(key)
        
        if not value:
            errors.append(ConfigError(key, rules['message'], rules['severity']))
            continue
            
        try:
            if not rules['validator'](value):
                errors.append(ConfigError(
                    key,
                    f"Invalid {key}: {rules['message']}",
                    rules['severity']
                ))
        except Exception as e:
            errors.append(ConfigError(
                key,
                f"Validation error for {key}: {str(e)}",
                'error'
            ))

    # Additional security checks
    if app.config.get('DEBUG', False) and app.config.get('ENV') == 'production':
        errors.append(ConfigError(
            'DEBUG',
            'Debug mode should not be enabled in production',
            'warning'
        ))

    return errors

def check_config(app: Flask, raise_on_warnings: bool = False) -> None:
    """Check configuration and raise error if invalid."""
    errors = validate_config(app)
    
    if errors:
        error_messages = []
        warning_messages = []
        
        for error in errors:
            message = f"- {error.key}: {error.message}"
            if error.severity == 'error':
                error_messages.append(message)
            else:
                warning_messages.append(message)
        
        if error_messages:
            raise ValueError(f"Configuration errors:\n{''.join(error_messages)}")
        elif warning_messages and raise_on_warnings:
            raise ValueError(f"Configuration warnings:\n{''.join(warning_messages)}")

def validate_url(url: str, required_scheme: str) -> bool:
    """Validate URL format and scheme."""
    try:
        result = urlparse(url)
        return all([
            result.scheme,
            result.netloc,
            result.scheme == required_scheme or result.scheme == required_scheme + 's'
        ])
    except Exception:
        return False