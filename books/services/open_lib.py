from datetime import datetime
from functools import lru_cache
from typing import Optional
from urllib.parse import quote  # For encoding URLs

import requests

from ..models.models import Book

# OpenLibrary API would like you to include a User-Agent header to identify your app
# and provide contact information in case they need to get in touch.
# https://openlibrary.org/dev/docs/api
HEADERS = {"User-Agent": "books/1.0 (jared@kravse.dev)"}


@lru_cache(maxsize=128)  # Cache results to avoid unnecessary API calls
def search_open_lib(query: str) -> list[Book]:
    """Search OpenLibrary for books matching the query."""
    url = f"https://openlibrary.org/search.json?q={quote(query)}"

    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()  # Raises error for HTTP issues
        data = response.json()

        # Extract book data, ensuring safe defaults
        books = data.get("docs", [])

        return [
            Book(
                title=book.get("title", "Unknown Title"),
                author=book.get("author_name", ["Unknown Author"])[0],
                date_read=None,
                cover_key=book.get("cover_i"),
                open_library_key=book.get("key"),
                first_publish_year=book.get("first_publish_year"),
            )
            for book in books
        ]

    except (requests.RequestException, ValueError) as e:
        print(f"Error searching OpenLibrary: {e}")
        return []  # Return empty list if API call fails


@lru_cache(maxsize=128)
def get_author_name_from_key(author: str) -> str:
    """Fetch author name from OpenLibrary API given an author key."""
    author_url = f"https://openlibrary.org{author}.json"
    try:
        response = requests.get(author_url, headers=HEADERS)
        response.raise_for_status()  # Raises HTTPError for bad responses (4xx, 5xx)
        return response.json().get("name", "")
    except (requests.RequestException, ValueError) as e:
        print(f"Error fetching author name: {e}")
        return "Unknown Author"  # Default fallback


@lru_cache(maxsize=128)
def get_book_from_key(key: str) -> Optional[Book]:
    """Fetch book details from OpenLibrary API given a book key."""
    url = f"https://openlibrary.org{key}.json"
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        details = response.json()

        # Handle missing authors safely
        authors = details.get("authors", [])
        author_key = authors[0]["author"]["key"] if authors else None
        author = (
            get_author_name_from_key(author_key) if author_key else "Unknown Author"
        )

        # Extract first publish year safely
        first_publish_year = details.get("first_publish_year") or details.get(
            "first_publish_date"
        )
        first_publish_year = (
            str(first_publish_year)[-4:] if first_publish_year else "Unknown"
        )

        # Extract cover key safely
        cover = details.get("covers", [None])[0]

        return Book(
            title=details.get("title", "Unknown Title"),
            author=author,
            date_read=datetime.now(),
            num_times_read=1,
            cover_key=cover,
            open_library_key=key,
            first_publish_year=first_publish_year,
        )
    except (requests.RequestException, ValueError) as e:
        print(f"Error fetching book details: {e}")
        return None  # Indicate failure instead of breaking
