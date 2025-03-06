import reflex as rx

nav_pages = {
    "Home": {"name": "Home", "path": "/"},
    "Search": {"name": "Search", "path": "/search"},
}


def nav() -> rx.Component:
    return rx.flex(
        *[
            rx.flex(
                rx.link(
                    page["name"],
                    href=page["path"],
                    text_decoration=rx.cond(
                        rx.State.router.page.path == page["path"],
                        "underline",
                        "none",
                    ),
                    color=rx.color("white"),
                ),
                rx.cond(
                    i == len(nav_pages) - 1,
                    rx.fragment(),
                    rx.text("|", margin_x="1rem"),
                ),
            )
            for i, page in enumerate(nav_pages.values())
        ],
        justify_content="space_between",
    )
