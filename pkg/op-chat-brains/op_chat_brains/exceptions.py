class OpChatBrainsException(Exception):
    """Base exception for OpChatBrains"""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class UnsupportedVectorstoreError(OpChatBrainsException):
    """Raised when an unsupported vectorstore is specified"""

    pass
