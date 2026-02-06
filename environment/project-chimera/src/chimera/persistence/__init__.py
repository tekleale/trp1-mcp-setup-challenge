"""
Persistence Module for Project Chimera.

Provides state persistence using Redis.

Spec Reference: specs/technical.md Section 2 (State Management)
"""

from .persistence import PersistenceManager

__all__ = ["PersistenceManager"]

