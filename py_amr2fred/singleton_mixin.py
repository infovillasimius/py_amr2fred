"""
Singleton Mixin for consistent singleton pattern implementation.

This module provides a thread-safe singleton mixin that can be inherited by classes
that need singleton behavior, replacing the inconsistent singleton implementations
throughout the codebase.
"""

import threading
from typing import Dict, Type, TypeVar, Optional

T = TypeVar('T', bound='SingletonMixin')


class SingletonMixin:
    """
    A thread-safe singleton mixin class.
    
    Classes that inherit from this mixin will have singleton behavior,
    ensuring only one instance exists per class type.
    
    Features:
    - Thread-safe instance creation
    - Per-class instance tracking
    - Lazy initialization
    - Memory efficient (instances only created when requested)
    """
    
    _instances: Dict[Type, object] = {}
    _lock = threading.Lock()
    
    def __new__(cls: Type[T], *args, **kwargs) -> T:
        """
        Create or return the singleton instance.
        
        Args:
            *args: Arguments passed to the constructor
            **kwargs: Keyword arguments passed to the constructor
            
        Returns:
            The singleton instance of the class
        """
        if cls not in cls._instances:
            with cls._lock:
                # Double-check locking pattern
                if cls not in cls._instances:
                    instance = super().__new__(cls)
                    cls._instances[cls] = instance
        
        return cls._instances[cls]
    
    @classmethod
    def get_instance(cls: Type[T], *args, **kwargs) -> T:
        """
        Get the singleton instance of the class.
        
        This method provides an explicit way to get the singleton instance
        and is compatible with existing get_* methods in the codebase.
        
        Args:
            *args: Arguments passed to the constructor
            **kwargs: Keyword arguments passed to the constructor
            
        Returns:
            The singleton instance of the class
        """
        instance = cls(*args, **kwargs)
        return instance
    
    @classmethod
    def clear_instance(cls) -> None:
        """
        Clear the singleton instance for this class.
        
        This is useful for testing or when you need to reset the singleton state.
        """
        with cls._lock:
            if cls in cls._instances:
                del cls._instances[cls]
    
    @classmethod
    def has_instance(cls) -> bool:
        """
        Check if an instance of this class exists.
        
        Returns:
            True if an instance exists, False otherwise
        """
        return cls in cls._instances
    
    @classmethod
    def clear_all_instances(cls) -> None:
        """
        Clear all singleton instances.
        
        This is useful for testing or application shutdown.
        Warning: This affects all classes using SingletonMixin.
        """
        with cls._lock:
            cls._instances.clear()