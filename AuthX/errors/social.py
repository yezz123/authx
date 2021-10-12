from AuthX.resources.social_messages import get_error_message


class SocialException(Exception):
    """
    This class is used to handle exceptions that are raised when a social

    Args:
        msg: The message that will be displayed to the user
        status_code: The status code that will be sent to the user
    """

    _base_url: str

    @classmethod
    def setup(cls, base_url: str) -> None:
        # TODO: Add a setup method to set the base url
        cls._base_url = base_url

    def __init__(self, msg: str, status_code: int, *args):
        # TODO: Add a __init__ method to set the message and status code
        self.content = get_error_message(msg, self._base_url)
        """
        The content that will be sent to the user
        """
        self.status_code = status_code
        """
        The status code that will be sent to the user
        """
        super().__init__(*args)
