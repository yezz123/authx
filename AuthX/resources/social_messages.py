class SocialErrorMessages:
    """
    Create SocialErrorMessages object
    """

    def __init__(self, base_url: str):
        self._full_messages = {
            "email facebook error": f"""<p>We can't get your email. Please, check <a href=\"https://facebook.com/settings\">your facebook settings</a>. Make sure you have email there.</p>
                <p><a href=\"{base_url}/login\">Back</p>
                """,
            "email exists": f"""<p>Email already exists.</p>
                <p><a href=\"{base_url}/login\">Back</p>
                """,
            "ban": f"""<p>User has been banned.</p>
                <p><a href=\"{base_url}/login\">Back</p>""",
        }
        self._server_error = "Unknown error"

    def get_error_message(self, msg: str) -> str:
        return self._full_messages.get(msg) or self._server_error


def get_error_message(msg: str, base_url: str) -> str:
    error_messages = SocialErrorMessages(base_url)
    return error_messages.get_error_message(msg)
