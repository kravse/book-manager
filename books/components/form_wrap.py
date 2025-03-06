import reflex as rx


def form_wrap(
    *args,
) -> rx.Component:
    """The login page.
    Returns:
        The UI for the about page.
    """
    return rx.flex(
        *args,
        direction="column",
        justify_content="center",
        width="100%",
    )
