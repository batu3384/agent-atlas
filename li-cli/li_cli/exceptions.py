"""li-cli errors."""


class LiCliError(Exception):
    """Base error."""


class AuthError(LiCliError):
    """Not logged in or session invalid."""


class ApiError(LiCliError):
    """LinkedIn HTTP/API error."""
