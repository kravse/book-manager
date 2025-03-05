# import time
import datetime
import os
import uuid

import reflex as rx
from sqlmodel import select

from ..models.models import User, User_Session


class AuthState(rx.State):
    auth_token: str = rx.Cookie(same_site="Strict", secure=True)

    @rx.var(cache=False)
    def authenticated_user(self) -> User:
        if self.auth_token == "":
            self.do_logout()
        with rx.session() as session:
            result = session.exec(
                select(User, User_Session).where(
                    User_Session.sess_id == self.auth_token,
                    User_Session.exp >= datetime.datetime.now(datetime.timezone.utc),
                    User.id == User_Session.u_id,
                ),
            ).first()
            if result:
                user, session = result
                return user
        return User(id=-1)

    @rx.var(cache=False)
    def is_authenticated(self) -> bool:
        return (
            self.auth_token != ""
            and self.authenticated_user.id is not None
            and self.authenticated_user.id >= 0
        )

    def do_logout(self) -> None:
        """Destroy AuthSessions associated with the auth_token."""
        with rx.session() as session:
            for auth_session in session.exec(
                User_Session.select().where(User_Session.sess_id == self.auth_token)
            ).all():
                session.delete(auth_session)
            session.commit()
        self.auth_token = ""

    def generate_auth_token(self) -> str:
        return str(uuid.UUID(bytes=os.urandom(16), version=4))

    def _login(
        self,
        user_id: int,
        expiration_delta: datetime.timedelta = datetime.timedelta(days=14),
    ) -> None:
        if self.is_authenticated:
            self.do_logout()
        if user_id < 0:
            return
        self.auth_token = self.generate_auth_token()
        with rx.session() as session:
            session.add(
                User_Session(
                    u_id=user_id,
                    sess_id=self.auth_token,
                    exp=datetime.datetime.now(datetime.timezone.utc) + expiration_delta,
                )
            )
            session.commit()
