"""
AIOS Quantum Cloud Integration module.

Provides IBM Cloud services integration:
- Cloud Object Storage for experiment persistence
- Cloud Functions for serverless execution (future)
"""

from .storage import CloudStorage, StorageConfig, get_storage

__all__ = [
    "CloudStorage",
    "StorageConfig",
    "get_storage",
]
