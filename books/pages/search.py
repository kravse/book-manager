import reflex as rx

from ..components.book_stack import book_stack
from ..components.site_page import site_page
from ..models.models import Book
from ..services.open_lib import search_open_lib


class SearchState(rx.State):
    """The app state."""

    book_query: list[Book] = []
    has_searched: bool = False
    visible_results: int = 10

    def search_for_book(self, data):
        """Get books from the API."""
        self.has_searched = True
        self.book_query = []
        try:
            key = next(iter(data))
            title = data[key]
            title = title.replace(" ", "+")
            self.book_query = search_open_lib(title)
        except StopIteration:  # Raised when iterating over an empty dict
            return rx.toast.error("No data provided.")
        except KeyError:  # Raised if key is not found
            return rx.toast.error(f"Error: Key '{key}' not found in data.")

    @rx.var(cache=True)
    def book_list(self) -> list[Book]:
        return self.book_query

    def clear(self):
        self.reset()


def book_form() -> rx.Component:
    """The book search form."""
    return rx.form(
        rx.form.field(
            rx.form.label("Add a book"),
            rx.flex(
                rx.form.control(
                    rx.input(
                        id="book_title", placeholder="Enter a book title", width="100%"
                    ),
                    as_child=True,
                    width="100%",
                ),
                rx.button("Search", type="submit", margin_left="1rem"),
                width="100%",
            ),
            width="100%",
        ),
        width="100%",
        on_submit=SearchState.search_for_book,
    )


@site_page(
    route="/search",
    title="",
)
def search() -> rx.Component:
    # Welcome Page (Index)
    return rx.box(
        rx.vstack(
            book_form(),
            rx.cond(
                SearchState.has_searched,
                rx.vstack(
                    rx.cond(
                        SearchState.book_list,
                        rx.foreach(
                            SearchState.book_list[: SearchState.visible_results],
                            lambda book: book_stack(book),
                        ),
                        rx.text("No books found."),
                    ),
                    padding="1rem",
                    height="500px",
                    overflow="auto",
                    background_color=rx.color("gray", 3),
                    columns="repeat(auto-fill, minmax(200px, 1fr))",
                    gap="1rem",
                    width="100%",
                ),
                rx.text(),
            ),
            width="100%",
        ),
        width="100%",
        on_mount=SearchState.clear,
    )
