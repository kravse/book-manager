import reflex as rx
import requests
from PIL import Image

from ..components.site_page import site_page


class book_meta(rx.Base):
    subjects: list[str] | None
    title: str | None
    author: str | None
    covers: list[int] | None
    description: dict | str | None
    ...


class AddState(rx.State):
    current_book_key = ""
    current_book_meta: book_meta = None
    current_author = rx.Component

    def get_author(self):
        first_author = next(iter(self.current_book_meta.authors))
        print(self.current_book_meta)
        author_url = f"https://openlibrary.org{first_author['author']['key']}.json"
        response = requests.get(author_url)
        self.current_book_meta.author = response.json().get("name", "")

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
                self.get_author()
            except Exception as e:
                self.current_book_key = ""
                return rx.toast.error(f"No book found.{e}")

    @rx.var(cache=True)
    def description(self) -> str:
        desc = self.current_book_meta.description
        if isinstance(desc, str):
            return desc
        if isinstance(desc, dict):
            return desc.get("value", "")
        return ""

    @rx.var(cache=True)
    def image(self) -> Image.Image:
        url = (
            f"https://covers.openlibrary.org/b/id/{self.current_book_meta.covers[0]}-L.jpg"
            if self.current_book_meta.covers
            else "/placeholder.png"
        )
        return Image.open(requests.get(url, stream=True).raw)


@site_page(
    route="/add",
    title="Add a Book",
)
def add() -> rx.Component:
    return rx.box(
        rx.flex(
            rx.image(
                src=AddState.image,
                object_fit="cover",
                max_width="200px",
            ),
            rx.box(
                rx.el.h3(
                    f"{AddState.current_book_meta.title} ({AddState.current_book_meta.author})",
                    text_align="center",
                    margin="1rem",
                ),
                rx.text(AddState.description),
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
