"""
Book Fetcher Capabilities

Fetch book information from various sources:
- Google Books API (free, stable, English/Chinese books)
- Douban (framework, requires custom implementation)

Convention: Tool names must be book_fetcher_{id}

Note: For LLM-based book info generation, use services/book_fetcher.py
      which combines LLM capability with book fetcher logic.
"""

import json
from typing import Optional

import httpx
from loguru import logger
from pydantic import Field

from reelforge.core.mcp_server import reelforge_mcp


@reelforge_mcp.tool(
    description="Fetch book information from Google Books API",
    meta={
        "reelforge": {
            "display_name": "Google Books",
            "description": "Fetch book info from Google Books (English/Chinese books)",
            "is_default": True,
        }
    },
)
async def book_fetcher_google(
    book_name: str = Field(description="Book name"),
    author: Optional[str] = Field(default=None, description="Author name (optional)"),
) -> str:
    """
    Fetch book information from Google Books API
    
    Free API, no key required. Works for both English and Chinese books.
    
    Args:
        book_name: Book name
        author: Author name (optional, for better search results)
    
    Returns:
        JSON string with book information:
        {
            "title": "Book title",
            "author": "Author name",
            "summary": "Book summary",
            "genre": "Category",
            "publication_year": "2018",
            "cover_url": "https://...",
            "isbn": "9781234567890"
        }
    
    Example:
        >>> info = await book_fetcher_google("Atomic Habits")
        >>> book = json.loads(info)
        >>> print(book['title'])
        Atomic Habits
    """
    logger.info(f"Fetching book info from Google Books: {book_name}")
    
    try:
        # Build search query
        query = book_name
        if author:
            query += f"+inauthor:{author}"
        
        # Call Google Books API
        async with httpx.AsyncClient() as client:
            url = "https://www.googleapis.com/books/v1/volumes"
            params = {
                "q": query,
                "maxResults": 1,
                "langRestrict": "zh-CN,en",  # Chinese and English
            }
            
            response = await client.get(url, params=params, timeout=10.0)
            response.raise_for_status()
            data = response.json()
        
        if "items" not in data or len(data["items"]) == 0:
            logger.warning(f"No results found for: {book_name}")
            raise ValueError(f"No results found for book: {book_name}")
        
        # Parse first result
        item = data["items"][0]
        volume_info = item.get("volumeInfo", {})
        
        book_info = {
            "title": volume_info.get("title", book_name),
            "author": ", ".join(volume_info.get("authors", [author or "Unknown"])),
            "summary": volume_info.get("description", "No description available"),
            "genre": ", ".join(volume_info.get("categories", ["Uncategorized"])),
            "publication_year": volume_info.get("publishedDate", "")[:4] if volume_info.get("publishedDate") else "",
            "cover_url": volume_info.get("imageLinks", {}).get("thumbnail", ""),
            "isbn": next(
                (id_info["identifier"] for id_info in volume_info.get("industryIdentifiers", []) 
                 if id_info["type"] in ["ISBN_13", "ISBN_10"]),
                ""
            ),
        }
        
        logger.info(f"✅ Successfully fetched from Google Books: {book_info['title']}")
        return json.dumps(book_info, ensure_ascii=False, indent=2)
        
    except httpx.HTTPError as e:
        logger.error(f"HTTP error fetching from Google Books: {e}")
        raise
    except Exception as e:
        logger.error(f"Error fetching from Google Books: {e}")
        raise


@reelforge_mcp.tool(
    description="Fetch book information from Douban (requires custom implementation)",
    meta={
        "reelforge": {
            "display_name": "豆瓣读书 (Douban)",
            "description": "Fetch book info from Douban (best for Chinese books) - requires custom implementation",
            "is_default": False,
        }
    },
)
async def book_fetcher_douban(
    book_name: str = Field(description="Book name"),
    author: Optional[str] = Field(default=None, description="Author name (optional)"),
) -> str:
    """
    Fetch book information from Douban
    
    NOTE: Douban official API is closed. This is a framework for custom implementation.
    
    You can implement this using:
    1. Third-party Douban API services
    2. Web scraping (be careful with rate limits)
    3. Cached database
    
    Args:
        book_name: Book name
        author: Author name (optional)
    
    Returns:
        JSON string with book information
    
    Example implementation:
        ```python
        # Option 1: Use third-party API
        async with httpx.AsyncClient() as client:
            url = "https://your-douban-api-service.com/search"
            params = {"q": book_name}
            response = await client.get(url, params=params)
            data = response.json()
            return json.dumps(data, ensure_ascii=False)
        
        # Option 2: Web scraping
        # Use BeautifulSoup + httpx to scrape Douban pages
        
        # Option 3: Pre-built database
        # Query your own book database
        ```
    """
    logger.error("book_fetcher_douban is not implemented")
    logger.info("To implement: Edit reelforge/capabilities/book_fetcher.py and add your logic")
    raise NotImplementedError(
        "book_fetcher_douban requires custom implementation. "
        "Please edit reelforge/capabilities/book_fetcher.py to add your Douban API integration."
    )

