import reflex as rx


def spinner() -> rx.Component:
    return rx.flex(
        rx.spinner(size="3"),
        width="100%",
        height="50vh",
        justify_content="center",
        align_items="center",
    )
