from datetime import datetime
from functools import lru_cache

import reflex as rx
import requests
from PIL import Image

from ..components.auth import AuthState
from ..components.site_page import site_page
from ..components.spinner import spinner
from ..models.models import Book


@lru_cache(maxsize=128)  # Set max size for the cache
def get_author(author: str) -> str:
    author_url = f"https://openlibrary.org{author}.json"
    response = requests.get(author_url)
    return response.json().get("name", "")

    ...


@lru_cache(maxsize=128)  # Set max size for the cache
def fetch_details(key: str) -> dict:
    url = f"https://openlibrary.org{key}.json"
    response = requests.get(url)
    return response.json()


class AddState(AuthState):
    current_book: Book = None
    current_author = rx.Component

    @rx.event
    def get_book_details(self):
        """Get books fom the API."""
        page_params = self.router.page.params
        key = page_params.get("book_key")
        if key:
            try:
                details = fetch_details(key)
                authors = next(iter(details["authors"]))
                author = get_author(authors["author"]["key"])
                first_publish_year = (
                    details.get("first_publish_year")
                    or details.get("first_publish_date")[-4:]
                    or None
                )

                self.current_book = Book(
                    title=details.get("title", ""),
                    author=author,
                    date_read=datetime.now(),
                    num_times_read=1,
                    cover_key=details.get("covers", [])[0],
                    open_library_key=key,
                    first_publish_year=first_publish_year,
                    user_id=self.authenticated_user.id,
                )
            except Exception as e:
                return rx.toast.error(f"No book found.{e}")

    def add_book(self):
        with rx.session() as session:
            try:
                session.add(self.current_book)
                session.commit()
                session.refresh(self.current_book)
            except Exception as e:
                return rx.toast.error(f"Failed to add book.{e}")

            return rx.redirect("/")

    @rx.var(cache=True)
    def image(self) -> Image.Image:
        url = (
            f"https://covers.openlibrary.org/b/id/{self.current_book.cover_key}-L.jpg"
            if self.current_book.cover_key
            else f"{self.router.page.host}/placeholder.png"
        )
        return Image.open(requests.get(url, stream=True).raw)


@site_page(
    route="/add",
    title="",
)
def add() -> rx.Component:
    return rx.cond(
        AddState.current_book,
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
                        f"{AddState.current_book.title} ({AddState.current_book.author})",
                        text_align="center",
                        margin="1rem",
                    ),
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
