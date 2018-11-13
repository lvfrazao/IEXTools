class IEXHISTException(Exception):
    """
    Base exception class for all exceptions defined in this package
    """

    pass


class RequestsException(IEXHISTException):
    """
    Exception wrapper for requests exceptions
    """

    pass


class ProtocolException(IEXHISTException):
    """
    Unexpected format while reading or manipulating IEX DEEP or TOPS data
    """

    pass
