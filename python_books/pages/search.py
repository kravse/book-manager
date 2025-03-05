from functools import lru_cache

import reflex as rx
import requests

from ..components.site_page import site_page


class book_entry(rx.Base):
    author_key: list[str] | None
    author_name: list[str] | None
    cover_edition_key: str | None
    cover_i: int | None
    edition_count: int | None
    first_publish_year: int | None
    has_fulltext: bool | None
    ia: list[str] | None
    ia_collection_s: str | None
    key: str | None
    language: list[str] | None
    lending_edition_s: str | None
    lending_identifier_s: str | None
    public_scan_b: bool | None
    title: str | None


class search_list(rx.Base):
    books: list[book_entry]

    def __len__(self) -> int:
        return len(self.books)


@lru_cache(maxsize=128)  # Set max size for the cache
def search_open_lib(query: str) -> search_list:
    url = f"https://openlibrary.org/search.json?q={query}"
    response = requests.get(url)
    books = response.json()["docs"]
    book_query = search_list(books=[])
    for book in books:
        book_query.books.append(book_entry(**book))
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
                            lambda book: rx.vstack(
                                rx.flex(
                                    rx.flex(
                                        rx.image(
                                            rx.cond(
                                                book["cover_i"],
                                                f"https://covers.openlibrary.org/b/id/{book['cover_i']}-M.jpg",
                                                "/placeholder.png",
                                            ),
                                            height="100px",
                                            object_fit="cover",
                                        ),
                                        width="75px",
                                        justify_content="center",
                                    ),
                                    rx.flex(
                                        rx.vstack(
                                            rx.text(
                                                f"{book['title']} - {book['author_name']}"
                                            ),
                                            rx.text(
                                                f"{book['first_publish_year']}",
                                                weight="bold",
                                            ),
                                            justify_content="space-between",
                                            width="100%",
                                            margin_left="1rem",
                                            grow=1,
                                        ),
                                        rx.link(
                                            rx.button("Add", margin_left="1rem"),
                                            href="/add?book_key=" + book["key"],
                                        ),
                                        justify_content="space-between",
                                        align_items="center",
                                        width="100%",
                                    ),
                                    grow=1,
                                    width="100%",
                                ),
                                rx.divider(),
                                width="100%",
                            ),
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
