"""
Exception classes for TGA service module.
"""

class TGAClientError(Exception):
    """Base exception for TGA client errors."""
    pass

class TGAAuthenticationError(TGAClientError):
    """Raised when authentication with TGA API fails."""
    pass

class TGAConnectionError(TGAClientError):
    """Raised when connection to TGA API fails."""
    pass
