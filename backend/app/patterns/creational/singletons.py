from __future__ import annotations
import threading
import os
import logging
from typing import Optional, Any

logger = logging.getLogger(__name__)

class _SingletonMeta(type):
    _instances: dict[type, Any] = {}
    _lock: threading.Lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]

class AuthServiceSingleton(metaclass=_SingletonMeta):

    def __init__(self):
        self._supabase_url: str = os.getenv("SUPABASE_URL", "")
        self._supabase_key: str = os.getenv("SUPABASE_ANON_KEY", "")
        self._jwt_secret: str = os.getenv("JWT_SECRET", "changeme")
        self._client: Optional[Any] = None
        logger.info("AuthServiceSingleton initialised")

    def get_client(self):
        """Return (or lazily create) the Supabase client."""
        if self._client is None:
            try:
                from supabase import create_client
                self._client = create_client(self._supabase_url, self._supabase_key)
            except Exception as exc:
                logger.warning(f"Could not create Supabase client: {exc}")
        return self._client

    def verify_token(self, token: str) -> dict | None:
        """
        Verify a Supabase JWT and return the payload, or None if invalid.
        """
        try:
            from jose import jwt, JWTError
            payload = jwt.decode(
                token,
                self._jwt_secret,
                algorithms=["HS256"],
                options={"verify_aud": False},
            )
            return payload
        except Exception:
            return None

class NotificationServiceSingleton(metaclass=_SingletonMeta):

    def __init__(self):
        self._supabase_url: str = os.getenv("SUPABASE_URL", "")
        self._service_key: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
        self._client: Optional[Any] = None
        self._notification_queue: list[dict] = []
        logger.info("NotificationServiceSingleton initialised")

    def get_service_client(self):
       
        if self._client is None:
            try:
                from supabase import create_client
                self._client = create_client(self._supabase_url, self._service_key)
            except Exception as exc:
                logger.warning(f"Could not create service client: {exc}")
        return self._client

    async def push_notification(
        self,
        user_id: str,
        notification_type: str,
        title: str,
        message: str,
        metadata: dict | None = None,
    ) -> dict | None:
       
        client = self.get_service_client()
        if client is None:
            logger.warning("Notification skipped — no Supabase client available")
            return None
        try:
            result = client.table("notifications").insert({
                "user_id": user_id,
                "type": notification_type,
                "title": title,
                "message": message,
                "metadata": metadata or {},
                "read": False,
            }).execute()
            return result.data[0] if result.data else None
        except Exception as exc:
            logger.error(f"Failed to push notification: {exc}")
            return None

    def get_unread_count(self, user_id: str) -> int:
        client = self.get_service_client()
        if not client:
            return 0
        try:
            result = (
                client.table("notifications")
                .select("id", count="exact")
                .eq("user_id", user_id)
                .eq("read", False)
                .execute()
            )
            return result.count or 0
        except Exception:
            return 0

class AIRecommendationEngineSingleton(metaclass=_SingletonMeta):

    def __init__(self):
        self._api_key: str = os.getenv("GEMINI_API_KEY", "")
        self._model_name: str = "gemini-2.0-flash"
        self._client: Optional[Any] = None
        self._model: Optional[Any] = None
        logger.info("AIRecommendationEngineSingleton initialised")

    def get_model(self):

        if self._model is None:
            if not self._api_key:
                logger.warning("GEMINI_API_KEY not set — AI features will be unavailable")
                return None
            try:
                import google.generativeai as genai
                genai.configure(api_key=self._api_key)
                for name in ["gemini-flash-lite-latest", "gemini-2.0-flash-lite", "gemini-2.0-flash"]:
                    try:
                        m = genai.GenerativeModel(name)
                        self._model = m
                        self._model_name = name
                        logger.info(f"Gemini model {name!r} loaded successfully")
                        break
                    except Exception:
                        continue
            except Exception as exc:
                logger.error(f"Could not load Gemini model: {exc}")
        return self._model

    def is_available(self) -> bool:
        return bool(self._api_key) and self.get_model() is not None

    async def generate_content(self, prompt: str) -> str | None:
        model = self.get_model()
        if model is None:
            return None
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as exc:
            logger.error(f"Gemini generation error: {exc}")
            try:
                import google.generativeai as genai
                fallback = genai.GenerativeModel("gemini-flash-lite-latest")
                res = fallback.generate_content(prompt)
                return res.text
            except Exception as fallback_err:
                logger.error(f"Fallback model error: {fallback_err}")
                return None
