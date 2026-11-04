"""
Database service layer — wraps all Supabase interactions.
"""

from __future__ import annotations
import os
import logging
from typing import Optional, Any

logger = logging.getLogger(__name__)

_supabase_client: Optional[Any] = None


def get_supabase():
    """Return (or lazily create) the Supabase client. Uses service-role key for server operations."""
    global _supabase_client
    if _supabase_client is None:
        url = os.getenv("SUPABASE_URL", "")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY", "")
        if url and key:
            try:
                from supabase import create_client
                _supabase_client = create_client(url, key)
                logger.info("Supabase client initialised")
            except Exception as exc:
                logger.warning(f"Supabase client init failed: {exc}")
    return _supabase_client


def get_service_supabase():
    """Service-role client (bypasses RLS) — for server-side writes."""
    url = os.getenv("SUPABASE_URL", "")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    if url and key:
        try:
            from supabase import create_client
            return create_client(url, key)
        except Exception as exc:
            logger.warning(f"Service client init failed: {exc}")
    return None
