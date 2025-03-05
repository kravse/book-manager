import reflex as rx

from ..components.site_page import site_page


@site_page(
    route="/",
    title="",
)
def index() -> rx.Component:
    return rx.container(
        rx.vstack(
            rx.text(
                "You don't have any books yet! ",
                rx.link("add some", href="/search"),
                " to get started.",
                text_align="center",
                width="100%",
            ),
            width="100%",
        )
    )
