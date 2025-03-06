import reflex as rx

from ..components.auth import AuthState
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
                        lambda book: rx.vstack(
                            rx.flex(
                                rx.flex(
                                    rx.image(
                                        src="/placeholder.png",
                                        alt="Book cover",
                                        height="100px",
                                        margin_right="1rem",
                                    ),
                                    rx.flex(
                                        rx.el.h4(f"{book['title']}"),
                                        rx.text(f"{book['author']}"),
                                        justify_content="space-between",
                                        direction="column",
                                    ),
                                ),
                                rx.text(f"{book['date_read']}"),
                                align_items="flex-end",
                                justify_content="space-between",
                                width="100%",
                            ),
                            rx.divider(),
                            width="100%",
                        ),
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
