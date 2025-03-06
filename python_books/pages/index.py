import reflex as rx

from ..components.auth import AuthState
from ..components.book_stack import book_stack
from ..components.site_page import site_page
from ..models.models import Book


class IndexState(AuthState):
    book_list: list[Book] = []

    @rx.var(cache=True)
    def books(self) -> list[Book]:
        with rx.session() as session:
            book_list = session.exec(
                Book.select().where(Book.user_id == self.authenticated_user.id)
            ).all()
        return book_list


@site_page(
    route="/",
    title="",
)
def index() -> rx.Component:
    return rx.cond(
        AuthState.is_authenticated,
        rx.container(
            rx.vstack(
                rx.cond(
                    IndexState.books,
                    rx.foreach(
                        IndexState.books,
                        lambda book: book_stack(book),
                    ),
                    rx.text(
                        "You don't have any books yet! ",
                        rx.link("add some", href="/search"),
                        " to get started.",
                        text_align="center",
                        width="100%",
                    ),
                ),
                width="100%",
            ),
        ),
        rx.fragment(),
    )
