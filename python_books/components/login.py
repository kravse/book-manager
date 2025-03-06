import functools

import reflex as rx

from ..models.models import User
from .auth import AuthState
from .form_wrap import form_wrap


class LoginState(AuthState):
    def logout(self):
        self.session = ""

    @rx.event
    def on_submit(self, auth_data):
        input_user = auth_data.get("name", "")
        input_password = auth_data.get("password", "")

        with rx.session() as session:
            try:
                user = session.exec(
                    User.select().where(User.name == input_user)
                ).one_or_none()

                if not user or not user.verify(input_password):
                    rx.toast.error("Incorrect username or password")
                    return
                user_id = user.id
                if user.id and user.enabled:
                    self._login(user_id)
            finally:
                session.close()


def login() -> rx.Component:
    """The login page.
    Returns:
        The UI for the about page.
    """
    return form_wrap(
        rx.el.h5("Log in"),
        rx.form.root(
            rx.form.field(
                rx.form.control(
                    rx.input(
                        type="text",
                        placeholder="User Name",
                        size="3",
                        width="100%",
                        required=True,
                    ),
                    as_child=True,
                ),
                name="name",
                reset_on_submit=True,
                gap="1rem",
                width="100%",
            ),
            rx.form.field(
                rx.form.control(
                    rx.input(
                        type="password",
                        placeholder="Password",
                        size="3",
                        width="100%",
                        required=True,
                    ),
                    as_child=True,
                ),
                name="password",
                reset_on_submit=True,
                gap="1rem",
                width="100%",
            ),
            rx.form.submit(
                rx.button("Log In"),
                as_child=True,
                width="100%",
            ),
            on_submit=LoginState.on_submit,
            width="100%",
        ),
        rx.text(
            "Don't have an account? ",
            rx.link("Register", href="/register"),
            size="1",
            margin_top="1rem",
        ),
    )


def login_gate(page):
    @functools.wraps(page)
    def gate() -> rx.Component:
        return rx.flex(
            rx.cond(
                AuthState.is_hydrated,
                rx.cond(
                    AuthState.is_authenticated,
                    page(),
                    login(),
                ),
                rx.spinner(),
            ),
            width="100%",
        )

    return gate
