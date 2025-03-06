import reflex as rx

from ..models.models import Book


class RatingState(rx.State):
    @rx.event
    def update_rating(self, new_rating, book_id):
        with rx.session() as session:
            try:
                book = session.exec(Book.select().where((Book.id == book_id))).first()
                book.rating = new_rating
                session.add(book)
                session.commit()
                # this is not good.
                return rx.redirect(self.router.page.full_raw_path, replace=True)
            except Exception as e:
                session.rollback()
                return rx.toast.error(f"Failed to update rating: {str(e)}")


def rating(book: Book) -> rx.Component:
    return rx.hstack(
        rx.foreach(
            range(5),
            lambda i: rx.button(
                rx.icon(
                    "star",
                    color="white",
                    size=22,
                    margin_right="0.05rem",
                    fill=rx.cond(i < book.rating, "white", ""),
                    _hover={"fill": "yellow", "color": "yellow"},
                ),
                background="transparent",
                _hover_background="transparent",
                variant="ghost",
                on_click=lambda: RatingState.update_rating(i + 1, book.id),
            ),
        ),
    )
