"""Welcome to Reflex! This file outlines the steps to create a basic app."""

import reflex as rx
import requests

from rxconfig import config


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


class book_list(rx.Base):
    books: list[book_entry]

    def __len__(self) -> int:
        return len(self.books)


class BookState(rx.State):
    """The app state."""

    book_query: book_list = book_list(books=[])
    has_searched: bool = False
    visible_results: int = 10

    def search_for_book(self, data):
        """Get books from the API."""
        self.has_searched = True
        self.book_query = book_list(books=[])
        try:
            key = next(iter(data))
            title = data[key]
            title = title.replace(" ", "+")
            url = f"https://openlibrary.org/search.json?q={title}"
            response = requests.get(url)
            books = response.json()["docs"]
            for book in books:
                self.book_query.books.append(book_entry(**book))

        except Exception as e:
            print(e)
            self.book_query = book_list(books=[])

    @rx.var(cache=True)
    def book_list(self) -> book_list:
        return self.book_query

    def clear(self):
        self.reset()


def book_form() -> rx.Component:
    """The book search form."""
    return rx.form(
        rx.form.field(
            rx.form.label("Book Title"),
            rx.flex(
                rx.form.control(
                    rx.input(id="book_title", placeholder="Enter a book title"),
                    as_child=True,
                    width="100%",
                ),
                rx.button("Search", type="submit", margin_left="1rem"),
                width="100%",
            ),
        ),
        on_submit=BookState.search_for_book,
    )


def index() -> rx.Component:
    # Welcome Page (Index)
    return rx.container(
        rx.vstack(
            rx.heading(
                "Search For a Book", width="100%", text_align="center", margin="1rem"
            ),
            book_form(),
            rx.cond(
                BookState.has_searched,
                rx.vstack(
                    rx.heading("Books"),
                    rx.vstack(
                        rx.cond(
                            BookState.book_list.books,
                            rx.foreach(
                                BookState.book_list.books[: BookState.visible_results],
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
                        width="100%",
                        background_color=rx.color("gray", 3),
                        columns="repeat(auto-fill, minmax(200px, 1fr))",
                        gap="1rem",
                    ),
                    width="100%",
                ),
                rx.fragment(),
            ),
        ),
        on_mount=BookState.clear,
    )


app = rx.App()
app.add_page(index)
