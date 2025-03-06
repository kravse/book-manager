import reflex as rx

from ..models.models import Book


def book_stack(book: Book) -> rx.Component:
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
                    rx.vstack(
                        rx.text(f"{book['title']} - {book['author']}"),
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
                        href="/add?book_key=" + book["open_library_key"],
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
