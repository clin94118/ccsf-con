class ProcessingError(Exception):
    """
    General Custom exception class for errors related to API processing.

    Attributes:
        message (str): Error message describing the issue.
        status_code (int): The HTTP status code associated with the error (if available).
        reason (str): The reason for the error (if available).
    """

    def __init__(self, message, status_code=None, reason=None):
        self.message = message
        self.status_code = status_code
        self.reason = reason
        super().__init__(self.message)

    def __str__(self):
        return f"ProcessingError: {self.message} (Status Code: {self.status_code}, Reason: {self.reason})"
