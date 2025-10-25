"""
Book Fetcher Service

Fetch book information from various sources (API or LLM).
"""

import json
from typing import Optional, Literal

from loguru import logger

from reelforge.services.base import BaseService


class BookFetcherService(BaseService):
    """
    Book information fetcher service
    
    Provides unified access to various book data sources:
    - API: Google Books, Douban, etc. (via configured capability)
    - LLM: Generate book info using LLM (flexible, works for any book)
    
    Usage:
        # Use default source (from config, usually 'google')
        book_info = await reelforge.book_fetcher("原则")
        
        # Explicitly use Google Books API
        book_info = await reelforge.book_fetcher("Atomic Habits", query_source="google")
        
        # Explicitly use LLM (good for Chinese books)
        book_info = await reelforge.book_fetcher("人性的弱点", query_source="llm")
        
        # Use Douban (if you implemented it)
        book_info = await reelforge.book_fetcher(
            book_name="原则",
            author="瑞·达利欧",
            query_source="douban"
        )
    """
    
    def __init__(self, config_manager):
        super().__init__(config_manager, "book_fetcher")
        self._core = None  # Will be set by ReelForgeCore (for LLM query)
    
    def set_core(self, core):
        """Set reference to ReelForgeCore (for LLM query)"""
        self._core = core
    
    async def __call__(
        self,
        book_name: str,
        author: Optional[str] = None,
        query_source: Optional[Literal["google", "douban", "llm"]] = None,
        **kwargs
    ) -> dict:
        """
        Fetch book information
        
        Args:
            book_name: Book name (required)
            author: Author name (optional, improves matching accuracy)
            query_source: Data source to query:
                - "google": Google Books API
                - "douban": Douban Books (requires implementation)
                - "llm": Generate book info using LLM
                - None: Use default from config (usually "google")
            **kwargs: Additional provider-specific parameters
        
        Returns:
            Book information dict with fields:
                - title: Book title
                - author: Author name
                - summary: Book summary
                - genre: Book category/genre
                - publication_year: Publication year (string)
                - key_points: List of key points (only from LLM)
                - cover_url: Cover image URL (only from API)
                - isbn: ISBN code (only from API)
                - source: Data source ("google", "douban", or "llm")
        
        Examples:
            >>> # Use default source (from config)
            >>> book = await reelforge.book_fetcher("Atomic Habits")
            
            >>> # Explicitly use Google Books
            >>> book = await reelforge.book_fetcher("Atomic Habits", query_source="google")
            
            >>> # Explicitly use LLM (good for Chinese books)
            >>> book = await reelforge.book_fetcher("人性的弱点", query_source="llm")
            
            >>> # Use Douban (if implemented)
            >>> book = await reelforge.book_fetcher(
            ...     "原则",
            ...     author="瑞·达利欧",
            ...     query_source="douban"
            ... )
            
            >>> print(f"Title: {book['title']}")
            >>> print(f"Source: {book['source']}")
        """
        # Route to appropriate method based on query_source
        if query_source == "llm":
            # Use LLM to generate book info
            return await self._fetch_via_llm(book_name, author)
        else:
            # Use API (google, douban, or default from config)
            return await self._fetch_via_api(book_name, author, query_source, **kwargs)
    
    async def _fetch_via_api(
        self,
        book_name: str,
        author: Optional[str] = None,
        query_source: Optional[str] = None,
        **kwargs
    ) -> dict:
        """
        Fetch book information via API capability
        
        Args:
            book_name: Book name
            author: Author name (optional)
            query_source: Specific capability to use ("google", "douban", or None for default)
            **kwargs: Additional parameters
        
        Returns:
            Book information dict
        
        Raises:
            Exception: If API call fails
        """
        params = {"book_name": book_name}
        if author is not None:
            params["author"] = author
        params.update(kwargs)
        
        # Call book_fetcher capability
        # If query_source is specified (e.g., "google"), use it
        # Otherwise use default from config
        result_json = await self._config_manager.call(
            self._capability_type,
            cap_id=query_source,  # None = use default from config
            **params
        )
        result = json.loads(result_json)
        result["source"] = query_source or self.active or "api"
        
        logger.info(f"✅ Fetched book info from {result['source']}: {result.get('title', book_name)}")
        return result
    
    async def _fetch_via_llm(self, book_name: str, author: Optional[str] = None) -> dict:
        """
        Generate book information using LLM
        
        This method uses LLM to generate book information based on its knowledge.
        Good for books that are not available in API databases or for Chinese books.
        
        Args:
            book_name: Book name
            author: Author name (optional)
        
        Returns:
            Book information dict
        
        Raises:
            ValueError: If LLM response cannot be parsed
            Exception: If LLM call fails
        """
        if not self._core:
            raise RuntimeError("ReelForgeCore not set. Cannot use LLM query.")
        
        # Build prompt
        author_info = f"，作者是{author}" if author else ""
        prompt = f"""请为书籍《{book_name}》{author_info}生成详细的书籍信息。

要求：
1. 如果你知道这本书，请提供真实准确的信息
2. 如果不确定，请基于书名和作者推测合理的信息
3. 严格按照JSON格式输出，不要添加任何其他内容

输出格式（JSON）：
{{
    "title": "书名",
    "author": "作者",
    "summary": "书籍简介（100-200字，概括核心内容和价值）",
    "genre": "书籍类型（如：自我成长、商业管理、心理学等）",
    "publication_year": "2018",
    "key_points": [
        "核心观点1（20-30字）",
        "核心观点2（20-30字）",
        "核心观点3（20-30字）"
    ]
}}

只输出JSON，不要其他内容。"""
        
        # Call LLM
        response = await self._core.llm(
            prompt=prompt,
            temperature=0.3,  # Lower temperature for more factual responses
            max_tokens=1000
        )
        
        # Parse JSON
        try:
            book_info = json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            logger.error(f"Response: {response[:200]}...")
            raise ValueError(f"LLM returned invalid JSON for book: {book_name}")
        
        # Ensure required fields exist
        book_info.setdefault("title", book_name)
        book_info.setdefault("author", author or "Unknown")
        book_info.setdefault("summary", "No summary available")
        book_info.setdefault("genre", "Unknown")
        book_info.setdefault("publication_year", "")
        book_info["source"] = "llm"
        
        logger.info(f"✅ Generated book info via LLM: {book_info['title']}")
        return book_info

