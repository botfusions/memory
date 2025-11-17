"""
BOTFUSIONS - MEMORI SERVICE
Core Memori business logic
"""

from memori import Memori
from openai import OpenAI
import os
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class MemoriService:
    """Memori service wrapper"""

    def __init__(
        self,
        database_url: str,
        openai_api_key: str,
        namespace: str = "default"
    ):
        """Initialize Memori service"""
        self.database_url = database_url
        self.openai_api_key = openai_api_key
        self.namespace = namespace

        # Memori instance
        self.memori = None
        self.openai_client = None

        logger.info(f"MemoriService initialized with namespace: {namespace}")

    def _ensure_memori(self):
        """Ensure Memori is initialized and enabled"""
        if self.memori is None:
            self.memori = Memori(
                database_connect=self.database_url,
                conscious_ingest=True,  # Short-term working memory
                auto_ingest=True,       # Dynamic search per query
                openai_api_key=self.openai_api_key,
                namespace=self.namespace
            )
            self.memori.enable()
            logger.info(f"Memori enabled for namespace: {self.namespace}")

        if self.openai_client is None:
            self.openai_client = OpenAI(api_key=self.openai_api_key)
            logger.info("OpenAI client initialized")

    def chat(
        self,
        message: str,
        user_id: Optional[str] = None,
        model: str = "gpt-4o-mini",
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Chat with memory

        Args:
            message: User message
            user_id: Optional user ID for multi-user isolation
            model: OpenAI model to use
            system_prompt: Optional system prompt

        Returns:
            Dict with response and metadata
        """
        # User-specific namespace
        if user_id:
            original_namespace = self.namespace
            self.namespace = f"{original_namespace}_user_{user_id}"
            self.memori = None  # Force re-initialization

        self._ensure_memori()

        # Build messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": message})

        # Call OpenAI with Memori
        try:
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=messages
            )

            result = {
                "success": True,
                "response": response.choices[0].message.content,
                "model": model,
                "namespace": self.namespace,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }

            logger.info(f"Chat successful - namespace: {self.namespace}, tokens: {response.usage.total_tokens}")
            return result

        except Exception as e:
            logger.error(f"Chat error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "namespace": self.namespace
            }

        finally:
            # Restore original namespace
            if user_id:
                self.namespace = original_namespace
                self.memori = None

    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        self._ensure_memori()

        return {
            "namespace": self.namespace,
            "database": self.database_url.split("@")[1].split("/")[0] if "@" in self.database_url else "unknown",
            "status": "active"
        }


# Singleton factory
_services: Dict[str, MemoriService] = {}


def get_memori_service(
    namespace: str = "default",
    user_id: Optional[str] = None
) -> MemoriService:
    """
    Get or create MemoriService instance

    Args:
        namespace: Base namespace
        user_id: Optional user ID for isolation

    Returns:
        MemoriService instance
    """
    # Create unique key
    if user_id:
        key = f"{namespace}_user_{user_id}"
    else:
        key = namespace

    # Get or create
    if key not in _services:
        _services[key] = MemoriService(
            database_url=os.getenv("MEMORI_DATABASE__CONNECTION_STRING"),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            namespace=key
        )

    return _services[key]
