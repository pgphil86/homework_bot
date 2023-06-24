class ApiError(Exception):
    """Not correct answer from API."""

    pass


class ResponseError(Exception):
    """Error of response."""

    pass


class ParseStatusError(Exception):
    """ParseStatuses error."""

    pass
