from functools import lru_cache

import reflex as rx
import requests

from ..components.book_stack import book_stack
from ..components.site_page import site_page
from ..models.models import Book

# class book_entry(rx.Base):
#     author_key: list[str] | None
#     author_name: list[str] | None
#     cover_edition_key: str | None
#     cover_i: int | None
#     edition_count: int | None
#     first_publish_year: int | None
#     has_fulltext: bool | None
#     ia: list[str] | None
#     ia_collection_s: str | None
#     key: str | None
#     language: list[str] | None
#     lending_edition_s: str | None
#     lending_identifier_s: str | None
#     public_scan_b: bool | None
#     title: str | None


class search_list(rx.Base):
    books: list[Book]

    def __len__(self) -> int:
        return len(self.books)


@lru_cache(maxsize=128)  # Set max size for the cache
def search_open_lib(query: str) -> search_list:
    url = f"https://openlibrary.org/search.json?q={query}"
    response = requests.get(url)
    books = response.json()["docs"]
    book_query = search_list(books=[])
    for book in books:
        author_metadata = book.get("author_name")
        author = None
        if author_metadata:
            author = author_metadata[0]

        book_query.books.append(
            Book(
                title=book.get("title"),
                author=author,
                date_read=None,
                cover_key=book.get("cover_i"),
                open_library_key=book.get("key"),
                first_publish_year=book.get("first_publish_year"),
            )
        )
    return book_query


class SearchState(rx.State):
    """The app state."""

    book_query: search_list = search_list(books=[])
    has_searched: bool = False
    visible_results: int = 10

    def search_for_book(self, data):
        """Get books from the API."""
        self.has_searched = True
        self.book_query = search_list(books=[])
        try:
            key = next(iter(data))
            title = data[key]
            title = title.replace(" ", "+")
            self.book_query = search_open_lib(title)
        except Exception as e:
            self.book_query = search_list(books=[])
            return rx.toast.error(f"No books found.{e}")

    @rx.var(cache=True)
    def book_list(self) -> search_list:
        return self.book_query

    def clear(self):
        self.reset()


def book_form() -> rx.Component:
    """The book search form."""
    return rx.form(
        rx.form.field(
            rx.form.label("Add a book"),
            rx.flex(
                rx.form.control(
                    rx.input(
                        id="book_title", placeholder="Enter a book title", width="100%"
                    ),
                    as_child=True,
                    width="100%",
                ),
                rx.button("Search", type="submit", margin_left="1rem"),
                width="100%",
            ),
            width="100%",
        ),
        width="100%",
        on_submit=SearchState.search_for_book,
    )


@site_page(
    route="/search",
    title="",
)
def search() -> rx.Component:
    # Welcome Page (Index)
    return rx.box(
        rx.vstack(
            book_form(),
            rx.cond(
                SearchState.has_searched,
                rx.vstack(
                    rx.cond(
                        SearchState.book_list.books,
                        rx.foreach(
                            SearchState.book_list.books[: SearchState.visible_results],
                            lambda book: book_stack(book),
                        ),
                        rx.text("No books found."),
                    ),
                    padding="1rem",
                    height="500px",
                    overflow="auto",
                    background_color=rx.color("gray", 3),
                    columns="repeat(auto-fill, minmax(200px, 1fr))",
                    gap="1rem",
                    width="100%",
                ),
                rx.text(),
            ),
            width="100%",
        ),
        width="100%",
        on_mount=SearchState.clear,
    )
