import reflex as rx
import requests
from PIL import Image
from sqlalchemy.exc import IntegrityError

from ..components.auth import AuthState
from ..components.rating import rating
from ..components.site_page import site_page
from ..components.spinner import spinner
from ..models.models import Book
from ..services.open_lib import get_book_from_key


class ViewState(AuthState):
    current_book: Book = Book()
    current_author = rx.Component

    @rx.event
    def get_book_details(self):
        """Get books fom the API."""
        page_params = self.router.page.params
        key = page_params.get("book_key")
        if key:
            book = get_book_from_key(key)
            if book:
                with rx.session() as session:
                    saved_book = session.exec(
                        Book.select().where(
                            (
                                Book.open_library_key == book.open_library_key
                                and Book.user_id == self.authenticated_user.id
                            )
                        )
                    ).first()
                    if saved_book:
                        self.current_book = saved_book
                    else:
                        book.user_id = self.authenticated_user.id
                        self.current_book = book
            else:
                return rx.toast.error("No book found.")

    def add_book(self):
        with rx.session() as session:
            try:
                session.add(self.current_book)
                session.commit()
                session.refresh(self.current_book)
            except IntegrityError:
                session.rollback()  # Rollback transaction to keep DB consistent
                return rx.toast.warning(
                    "You've already added this book to your reading list."
                )
            except Exception as e:
                session.rollback()
                return rx.toast.error(f"Failed to add book: {str(e)}")

            return rx.redirect("/")

    @rx.var(cache=True)
    def image(self) -> Image.Image | None:
        url = (
            f"https://covers.openlibrary.org/b/id/{self.current_book.cover_key}-L.jpg"
            if self.current_book.cover_key
            else f"{self.router.page.host}/placeholder.png"
            if self.router.page.host
            else None
        )
        return Image.open(requests.get(url, stream=True).raw) if url else None


def rating_if_exists() -> rx.Component:
    return rx.cond(
        ViewState.current_book.id,
        rx.fragment(
            rx.text("My Rating: ", margin_right="1rem"),
            rating(ViewState.current_book),
        ),
        None,
    )


@site_page(
    route="/view",
    title="",
)
def view() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.cond(
                ViewState.image,
                rx.image(
                    src=ViewState.image,
                    object_fit="cover",
                    max_width="200px",
                ),
                None,
            ),
            rx.button(
                "Add This Book",
                variant="outline",
                on_click=ViewState.add_book,
            ),
            rx.el.h3(
                f"{ViewState.current_book.title} ({ViewState.current_book.author})",
                text_align="center",
                margin="1rem",
            ),
            rx.grid(
                rx.text("Published: "),
                rx.text(ViewState.current_book.first_publish_year),
                rating_if_exists(),
                align="center",
                justify="center",
                columns="2",
                spacing="2",
                width="500px",
            ),
            direction="column",
            justify_content="center",
            align_items="center",
            width="100%",
            gap="1rem",
        ),
        width="100%",
        on_mount=ViewState.get_book_details,
    )
