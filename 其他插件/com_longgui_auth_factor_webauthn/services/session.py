from django.http import HttpRequest


class SessionService:
    # def start_session(self, *, request: HttpRequest) -> None:
    #     """
    #     Start a session so that we have a unique ID we can associate options with, even when
    #     we don't have a username
    #     """
    #     if not request.session.exists(request.session.session_key):
    #         request.session.create()
    #         request.session.set_expiry(0)

    # def log_in_user(self, *, request: HttpRequest, username: str) -> None:
    #     """
    #     Use a session cookie to temporarily remember the user
    #     """
    #     request.session["username"] = username

    # def log_out_user(self, *, request: HttpRequest) -> None:
    #     """
    #     Annihilate the user's session so we can forget about them
    #     """
    #     request.session.flush()

    # def user_is_logged_in(self, *, request: HttpRequest) -> bool:
    #     try:
    #         username = request.session["username"]
    #         return username is not None
    #     except KeyError:
    #         pass

    #     return False

    def get_session_key(self, *, request: HttpRequest) -> str:
        key = request.session.session_key

        if not key:
            raise Exception("Attempted to get session key before session was created")

        return key
