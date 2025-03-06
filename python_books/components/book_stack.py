import reflex as rx


def book_stack(book) -> rx.Component:
    return (
        rx.vstack(
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
                        rx.text(f"{book['title']} - {book['author_name']}"),
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
    )
