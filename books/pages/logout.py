import reflex as rx

from ..components.auth import AuthState
from ..components.site_page import site_page


@site_page(
    route="/logout",
    title="",
)
def logout() -> rx.Component:
    return rx.fragment(on_mount=AuthState.do_logout)
