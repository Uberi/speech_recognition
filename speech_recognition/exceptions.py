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
    """
    pass
