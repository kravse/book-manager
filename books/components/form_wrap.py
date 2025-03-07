import reflex as rx


def form_wrap(
    *args,
) -> rx.Component:
    return rx.flex(
        *args,
        direction="column",
        justify_content="center",
        width="100%",
    )
