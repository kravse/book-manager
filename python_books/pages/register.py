import reflex as rx

from ..components.auth import AuthState
from ..components.form_wrap import form_wrap
from ..components.site_page import site_page
from ..models.models import User


class RegisterState(AuthState):
    @staticmethod
    def register(username: str, password: str) -> None:
        with rx.session() as session:
            session.add(
                User(
                    name=username,
                    pw_hash=User.hash_password(password),
                    enabled=True,
                )
            )
            session.commit()

    @rx.event
    def on_submit(self, auth_data):
        input_user = auth_data.get("name", "")
        input_password = auth_data.get("password", "")
        if not input_user or not input_password:
            return rx.toast.error("Please provide a username and password")

        if len(input_password) < 8:
            return rx.toast.error("Password must be at least 8 characters")

        with rx.session() as session:
            user = session.exec(
                User.select().where(User.name == input_user)
            ).one_or_none()

        if user is not None:
            return rx.toast.error("User already exists")
        else:
            self.register(input_user, input_password)
            return rx.redirect("/")


@site_page(
    route="/register",
    title="Register",
    login_gated=False,
)
def register() -> rx.Component:
    return form_wrap(
        rx.el.h5("Register"),
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
            ),
            rx.form.submit(
                rx.button("Register"),
                as_child=True,
                width="100%",
            ),
            rx.text(
                "Go back to ",
                rx.link("log In", href="/"),
                ".",
                size="1",
                margin_top="1rem",
            ),
            on_submit=RegisterState.on_submit,
        ),
    )
