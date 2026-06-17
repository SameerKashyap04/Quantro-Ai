"""
Quantro Personal AI — Custom Exceptions
Application-specific exceptions with HTTP status codes.
"""
from fastapi import HTTPException, status


class QuantroException(HTTPException):
    """Base exception for Quantro application."""

    def __init__(self, detail: str, status_code: int = 500):
        super().__init__(status_code=status_code, detail=detail)


class AuthenticationError(QuantroException):
    """Authentication failed."""

    def __init__(self, detail: str = "Invalid credentials"):
        super().__init__(detail=detail, status_code=status.HTTP_401_UNAUTHORIZED)


class AuthorizationError(QuantroException):
    """Insufficient permissions."""

    def __init__(self, detail: str = "Not authorized"):
        super().__init__(detail=detail, status_code=status.HTTP_403_FORBIDDEN)


class NotFoundError(QuantroException):
    """Resource not found."""

    def __init__(self, resource: str = "Resource"):
        super().__init__(detail=f"{resource} not found", status_code=status.HTTP_404_NOT_FOUND)


class ValidationError(QuantroException):
    """Input validation failed."""

    def __init__(self, detail: str = "Validation error"):
        super().__init__(detail=detail, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


class RiskViolationError(QuantroException):
    """Trade violates risk management rules."""

    def __init__(self, detail: str = "Trade blocked by risk management"):
        super().__init__(detail=detail, status_code=status.HTTP_409_CONFLICT)


class BrokerError(QuantroException):
    """Broker API error."""

    def __init__(self, detail: str = "Broker API error"):
        super().__init__(detail=detail, status_code=status.HTTP_502_BAD_GATEWAY)


class EmergencyHaltError(QuantroException):
    """Trading halted due to emergency conditions."""

    def __init__(self, detail: str = "Trading halted — emergency drawdown protection active"):
        super().__init__(detail=detail, status_code=status.HTTP_423_LOCKED)
