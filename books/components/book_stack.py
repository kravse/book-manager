import reflex as rx

from ..models.models import Book
from .rating import rating


def book_stack(book: Book, show_rating: bool = False) -> rx.Component:
    return (
        rx.vstack(
            rx.flex(
                rx.flex(
                    rx.image(
                        rx.cond(
                            book["cover_key"],
                            f"https://covers.openlibrary.org/b/id/{book['cover_key']}-M.jpg",
                            "/placeholder.png",
                        ),
                        height="100px",
                        object_fit="cover",
                    ),
                    width="75px",
                    justify_content="center",
                ),
                rx.flex(
                    rx.flex(
                        rx.text(f"{book['title']} - {book['author']}"),
                        rx.text(
                            f"{book['first_publish_year']}",
                            weight="bold",
                        ),
                        justify_content="space-between",
                        flex_direction="column",
                        width="100%",
                        height="100%",
                        margin_left="1rem",
                    ),
                    rx.cond(show_rating, rating(book), None),
                    rx.link(
                        rx.button("View", margin_left="1rem"),
                        href="/view?book_key=" + book["open_library_key"],
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
    )
