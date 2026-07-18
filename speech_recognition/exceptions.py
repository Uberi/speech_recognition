class SetupError(Exception):
    pass


class WaitTimeoutError(Exception):
    pass


class RequestError(Exception):
    pass


class UnknownValueError(Exception):
    pass


class TranscriptionNotReady(Exception):
    pass


class TranscriptionFailed(Exception):
    pass


class RateLimitError(RequestError):
    """Raised when the speech recognition service returns an HTTP 429
    (Too Many Requests) response, indicating the caller has been rate
    limited.

    :attr retry_after: The number of seconds to wait before retrying,
        parsed from the response's ``Retry-After`` header if present,
        otherwise ``None``.
    """

    def __init__(self, message: str, retry_after: float | None = None):
        super().__init__(message)
        self.retry_after = retry_after
