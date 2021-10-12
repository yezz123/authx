class User:
    """
    Setup the user object
    """

    def __init__(self, data=None):
        """
        Initialize the user object

        Args:
            data (dict): A dictionary containing the user's data
        """
        self.data = data
        if data is None:
            self.is_authenticated = False
            self.is_admin = False
            self.id = None
            self.username = None
        else:
            self.is_authenticated = True
            self.is_admin = "admin" in self.data.get("permissions")
            self.id = int(self.data.get("id"))
            self.username = self.data.get("username")

    @classmethod
    async def create(cls, token: str, backend):
        """
        Create a user object from a token

        Args:
            token (str): The token to create the user object from
            backend (AuthX): The backend to use to create the user object
        Returns:
            User: The user object
        """
        data = await backend.decode_token(token)
        return cls(data)
