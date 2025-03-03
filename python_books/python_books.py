"""Welcome to Reflex! This file outlines the steps to create a basic app."""

import reflex as rx
import requests

from rxconfig import config

from .components.search import search

app = rx.App()


def index() -> rx.Component:
    return rx.container(
        rx.vstack(
            rx.heading("My Booklist", width="100%", text_align="center", margin="1rem"),
            rx.popover.root(
                rx.popover.trigger(
                    rx.button("Add a Book", margin="1rem"),
                ),
                rx.popover.content(
                    search(),
                ),
            ),
        )
    )


app.add_page(index)
