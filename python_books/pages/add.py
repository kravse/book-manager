import reflex as rx
import requests

from ..components.site_page import site_page


class book_meta(rx.Base):
    subjects: list[str] | None
    title: str | None
    author: str | None
    covers: list[int] | None
    description: dict | None
    ...


class AddState(rx.State):
    current_book_key = ""
    current_book_meta: book_meta = None
    current_author = rx.Component

    def get_book_details(self):
        """Get books from the API."""
        page_params = self.router.page.params
        key = page_params.get("book_key")
        if key and key != self.current_book_key:
            try:
                url = f"https://openlibrary.org{key}.json"
                response = requests.get(url)
                self.current_book_meta = book_meta(**response.json())
                self.current_book_key = key
                first_author = next(iter(self.current_book_meta.authors))
                author_url = (
                    f"https://openlibrary.org{first_author['author']['key']}.json"
                )
                response = requests.get(author_url)
                self.current_book_meta.author = response.json().get("name", "")
            except Exception as e:
                self.current_book_key = ""
                return rx.toast.error(f"No book found.{e}")


@site_page(
    route="/add",
    title="Add a Book",
)
def add() -> rx.Component:
    return rx.box(
        rx.flex(
            rx.image(
                rx.cond(
                    AddState.current_book_meta.covers[0],
                    f"https://covers.openlibrary.org/b/id/{AddState.current_book_meta.covers[0]}-L.jpg",
                    "/placeholder.png",
                ),
                object_fit="cover",
                max_width="200px",
            ),
            rx.box(
                rx.el.h3(
                    f"{AddState.current_book_meta.title} ({AddState.current_book_meta.author})",
                    text_align="center",
                    margin="1rem",
                ),
                rx.text(AddState.current_book_meta.description["value"]),
                margin_left="1rem",
                width="500px",
                max_width="100%",
            ),
            direction="column",
            justify_content="center",
            align_items="center",
            width="100%",
        ),
        width="100%",
        on_mount=AddState.get_book_details,
    )
