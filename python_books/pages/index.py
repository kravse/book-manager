import reflex as rx

from ..components.site_page import site_page
from ..models.models import BookList


class IndexState(rx.State):
    book_list: list[BookList] = []

    def get_books(self):
        with rx.session() as session:
            self.book_list = session.exec(BookList.select()).all()


@site_page(
    route="/",
    title="",
)
def index() -> rx.Component:
    return rx.container(
        rx.vstack(
            rx.foreach(
                IndexState.book_list,
                lambda book: rx.text(f"{book['title']}"),
            ),
            rx.text(
                "You don't have any books yet! ",
                rx.link("add some", href="/search"),
                " to get started.",
                text_align="center",
                width="100%",
            ),
            width="100%",
        ),
        on_mount=IndexState.get_books,
    )
