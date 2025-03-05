"""Welcome to Reflex! This file outlines the steps to create a basic app."""

import reflex as rx

from .pages import *

app = rx.App(
    stylesheets=[
        "/styles.css",
    ],
    theme=rx.theme(
        appearance="dark",
        has_background=True,
        accent_color="sky",
    ),
)
import os
