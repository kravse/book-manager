import reflex as rx

from ..components.auth import AuthState
from ..components.site_page import site_page
from ..models.models import BookList


class IndexState(AuthState):
    book_list: list[BookList] = []

    @rx.var(cache=True)
    def books(self) -> list[BookList]:
        with rx.session() as session:
            book_list = session.exec(
                BookList.select().where(BookList.user_id == self.authenticated_user.id)
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
                            rx.text(f"{book['title']}"),
                            rx.text(f"{book['author']}"),
                            rx.divider(),
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
