from datetime import datetime
from functools import lru_cache

import reflex as rx
import requests
from PIL import Image

from ..components.auth import AuthState
from ..components.site_page import site_page
from ..components.spinner import spinner
from ..models.models import Book


class book_meta(rx.Base):
    subjects: list[str] | None
    title: str | None
    author: str | None
    covers: list[int] | None
    description: dict | str | None
    ...


@lru_cache(maxsize=128)  # Set max size for the cache
def get_author(author: str) -> str:
    author_url = f"https://openlibrary.org{author}.json"
    response = requests.get(author_url)
    return response.json().get("name", "")

    ...


@lru_cache(maxsize=128)  # Set max size for the cache
def get_book_details(key: str) -> book_meta:
    url = f"https://openlibrary.org{key}.json"
    response = requests.get(url)
    return book_meta(**response.json())


class AddState(AuthState):
    current_book_key = ""
    current_book_meta: book_meta = None
    current_author = rx.Component

    def get_author(self):
        first_author = next(iter(self.current_book_meta.authors))
        self.current_book_meta.author = get_author(first_author["author"]["key"])

    def get_book_details(self):
        """Get books fom the API."""
        page_params = self.router.page.params
        key = page_params.get("book_key")
        if key:
            try:
                self.current_book_meta = get_book_details(key)
                self.current_book_key = key
                self.get_author()
            except Exception as e:
                self.current_book_key = ""
                return rx.toast.error(f"No book found.{e}")

    def add_book(self):
        with rx.session() as session:
            try:
                session.add(
                    Book(
                        title=self.current_book_meta.title,
                        author=self.current_book_meta.author,
                        date_read=datetime.now(),
                        num_times_read=1,
                        open_library_key=self.current_book_key,
                        user_id=self.authenticated_user.id,
                    )
                )
                session.commit()
            except Exception as e:
                return rx.toast.error(f"Failed to add book.{e}")

            return rx.redirect("/")

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
            else f"{self.router.page.host}/placeholder.png"
        )
        return Image.open(requests.get(url, stream=True).raw)


@site_page(
    route="/add",
    title="",
)
def add() -> rx.Component:
    return rx.cond(
        AddState.current_book_meta,
        rx.box(
            rx.vstack(
                rx.image(
                    src=AddState.image,
                    object_fit="cover",
                    max_width="200px",
                ),
                rx.button(
                    "Add This Book",
                    variant="outline",
                    on_click=AddState.add_book,
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
                gap="1rem",
            ),
            width="100%",
            on_mount=AddState.get_book_details,
        ),
        spinner(),
    )
