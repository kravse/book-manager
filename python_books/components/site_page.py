from collections.abc import Callable

import reflex as rx
from reflex.event import BASE_STATE, EventType

from .auth import AuthState
from .footer import footer
from .login import login_gate
from .nav import nav


def main_content(component: rx.Component, title: str) -> rx.Component:
    return rx.container(
        rx.flex(
            rx.flex(
                rx.el.h1("My Booklist"),
                rx.cond(
                    AuthState.is_authenticated,
                    rx.flex(
                        rx.el.h3(title),
                        nav(),
                        width="100%",
                        direction="column",
                        align_items="center",
                        justify_content="center",
                    ),
                    rx.fragment(),
                ),
                direction="column",
                align_items="center",
                justify_content="center",
                width="100%",
            ),
            component,
            width="100%",
            direction="column",
            align_items="center",
            height="90vh",
        ),
        footer(),
        width="100%",
    )


def site_page(
    route: str,
    title: str,
    login_gated: bool = True,
    on_load: EventType[[], BASE_STATE] | None = None,  # type: ignore
):
    """The template decorator.

    This decorator is used to create a template for all pages.
    It includes login requirements, a sidebar, and a main content area.
    It also sets metadata for the browser.
    """

    def decorator(page: Callable[[], rx.Component]) -> rx.Component:
        # all pages require login
        if login_gated:
            the_page = login_gate(page)
        else:
            the_page = page

        return rx.hstack(
            main_content(the_page(), title),
            width="100%",
            gap="0",
        )

    return lambda page: rx.page(
        route=route,
        # image="",
        title=title,
        on_load=on_load,
    )(decorator(page))
