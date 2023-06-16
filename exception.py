class MessageError(Exception):
    """Bot can't send messages."""

    pass


class ApiError(Exception):
    """Not correct answer from API."""

    pass


class EnvVariablesError(Exception):
    """Некорретные переменные окружения."""

    pass


class ResponseError(Exception):
    """Error of response."""

    pass


class ParseStatusError(Exception):
    """ParseStatuses error."""

    pass
