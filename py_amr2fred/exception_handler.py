"""
Centralized Exception Handling System

This module provides a decorator-based approach to standardize exception handling
across the codebase, replacing repeated try-catch blocks with logger.warning() calls.
"""

import functools
import logging
from typing import Any, Callable, Optional, Type, Union, Tuple
from enum import Enum

logger = logging.getLogger(__name__)


class LogLevel(Enum):
    """Enumeration of logging levels."""
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


def handle_exceptions(
    exception_types: Union[Type[Exception], Tuple[Type[Exception], ...]] = Exception,
    default_return: Any = None,
    log_level: Union[LogLevel, int] = LogLevel.WARNING,
    log_message: Optional[str] = None,
    reraise: bool = False,
    suppress_traceback: bool = True
) -> Callable:
    """
    Decorator to handle exceptions in a standardized way.
    
    This decorator replaces repeated try-catch blocks throughout the codebase
    with a consistent exception handling approach.
    
    Args:
        exception_types: Exception type or tuple of exception types to catch
        default_return: Value to return when an exception is caught
        log_level: Logging level to use (LogLevel enum or int)
        log_message: Custom log message template. Use {exception} for exception details
        reraise: Whether to reraise the exception after logging
        suppress_traceback: Whether to suppress traceback in logs
        
    Returns:
        Decorated function
        
    Example:
        @handle_exceptions(default_return=None, log_level=LogLevel.WARNING)
        def risky_function():
            # Implementation that might raise exceptions
            pass
            
        @handle_exceptions(
            exception_types=(FileNotFoundError, PermissionError),
            default_return=[],
            log_message="Failed to read file: {exception}"
        )
        def read_file():
            # File reading implementation
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exception_types as e:
                # Prepare log message
                if log_message:
                    message = log_message.format(exception=str(e))
                else:
                    message = f"Exception in {func.__name__}: {str(e)}"
                
                # Get logging level value
                level = log_level.value if isinstance(log_level, LogLevel) else log_level
                
                # Log the exception
                if suppress_traceback:
                    logger.log(level, message)
                else:
                    logger.log(level, message, exc_info=True)
                
                # Reraise if requested
                if reraise:
                    raise
                
                # Return default value
                return default_return
                
        return wrapper
    return decorator


def handle_file_operations(
    default_return: Any = None,
    log_level: LogLevel = LogLevel.WARNING
) -> Callable:
    """
    Specialized decorator for file operations.
    
    Handles common file-related exceptions with appropriate logging.
    
    Args:
        default_return: Value to return when an exception occurs
        log_level: Logging level to use
        
    Returns:
        Decorated function
    """
    return handle_exceptions(
        exception_types=(FileNotFoundError, PermissionError, OSError, IOError),
        default_return=default_return,
        log_level=log_level,
        log_message="File operation failed: {exception}"
    )


def handle_json_operations(
    default_return: Any = None,
    log_level: LogLevel = LogLevel.WARNING
) -> Callable:
    """
    Specialized decorator for JSON operations.
    
    Handles JSON parsing and encoding exceptions.
    
    Args:
        default_return: Value to return when an exception occurs
        log_level: Logging level to use
        
    Returns:
        Decorated function
    """
    import json
    
    return handle_exceptions(
        exception_types=(json.JSONDecodeError, json.JSONEncodeError),
        default_return=default_return,
        log_level=log_level,
        log_message="JSON operation failed: {exception}"
    )


def handle_network_operations(
    default_return: Any = None,
    log_level: LogLevel = LogLevel.WARNING,
    timeout_return: Any = None
) -> Callable:
    """
    Specialized decorator for network operations.
    
    Handles common network-related exceptions.
    
    Args:
        default_return: Value to return for general exceptions
        log_level: Logging level to use
        timeout_return: Value to return specifically for timeout exceptions
        
    Returns:
        Decorated function
    """
    import requests
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except requests.exceptions.Timeout as e:
                level = log_level.value if isinstance(log_level, LogLevel) else log_level
                logger.log(level, f"Network timeout in {func.__name__}: {str(e)}")
                return timeout_return if timeout_return is not None else default_return
            except (
                requests.exceptions.RequestException,
                requests.exceptions.ConnectionError,
                requests.exceptions.HTTPError
            ) as e:
                level = log_level.value if isinstance(log_level, LogLevel) else log_level
                logger.log(level, f"Network error in {func.__name__}: {str(e)}")
                return default_return
                
        return wrapper
    return decorator


class RecursionGuard:
    """
    Context manager for preventing infinite recursion.
    
    Replaces manual recursion counters with automatic cleanup.
    
    Example:
        with RecursionGuard("function_name", max_depth=100):
            # Implementation that might recurse
            pass
    """
    
    _counters = {}
    
    def __init__(self, context_name: str, max_depth: int = 1000):
        """
        Initialize recursion guard.
        
        Args:
            context_name: Name to identify the recursion context
            max_depth: Maximum allowed recursion depth
        """
        self.context_name = context_name
        self.max_depth = max_depth
        self.depth = 0
    
    def __enter__(self):
        """Enter the recursion context."""
        self.depth = self._counters.get(self.context_name, 0) + 1
        
        if self.depth > self.max_depth:
            raise RecursionError(f"Maximum recursion depth exceeded in {self.context_name}")
        
        self._counters[self.context_name] = self.depth
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the recursion context."""
        self._counters[self.context_name] -= 1
        if self._counters[self.context_name] <= 0:
            del self._counters[self.context_name]


def recursion_guard(max_depth: int = 1000):
    """
    Decorator to prevent infinite recursion.
    
    Args:
        max_depth: Maximum allowed recursion depth
        
    Returns:
        Decorated function
        
    Example:
        @recursion_guard(max_depth=100)
        def recursive_function():
            # Implementation that might recurse
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            context_name = f"{func.__module__}.{func.__name__}"
            with RecursionGuard(context_name, max_depth):
                return func(*args, **kwargs)
        return wrapper
    return decorator