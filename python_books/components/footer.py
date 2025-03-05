import reflex as rx

from .auth import AuthState


def footer() -> rx.Component:
    return rx.flex(
        rx.cond(
            AuthState.is_authenticated,
            rx.button(
                "Log Out",
                margin="1rem",
                on_click=AuthState.do_logout,
                variant="ghost",
                color=rx.color("white"),
            ),
            rx.fragment(),
        ),
        rx.color_mode.button(),
        justify_content="center",
        align_items="center",
    )
