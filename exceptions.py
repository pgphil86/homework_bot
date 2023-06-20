class MessageError(Exception):
    """Bot can't send messages."""

    pass


class ApiError(Exception):
    """Not correct answer from API."""

    pass


class EnvironmentError(Exception):
    """Error of environment objects."""

    pass


class ResponseError(Exception):
    """Error of response."""

    pass


class ParseStatusError(Exception):
    """ParseStatuses error."""

    pass
