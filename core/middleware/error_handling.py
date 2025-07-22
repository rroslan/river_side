import logging
import socket
from django.http import Http404
from django.core.exceptions import PermissionDenied
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)

class BrokenPipeErrorMiddleware(MiddlewareMixin):
    """
    Middleware to handle broken pipe errors gracefully in development.

    Broken pipe errors occur when a client disconnects before the server
    finishes sending a response. This is common during development when
    refreshing pages or navigating away quickly.
    """

    def process_exception(self, request, exception):
        """
        Handle broken pipe and connection reset errors silently
        """
        # Check if it's a broken pipe or connection reset error
        if isinstance(exception, (BrokenPipeError, ConnectionResetError)):
            logger.debug(f"Client disconnected: {exception}")
            return None

        # Check for socket errors that indicate client disconnection
        if isinstance(exception, socket.error):
            if exception.errno in (32, 104):  # EPIPE, ECONNRESET
                logger.debug(f"Socket error (client disconnected): {exception}")
                return None

        # Let other exceptions propagate normally
        return None

    def process_response(self, request, response):
        """
        Process the response normally
        """
        return response

class CleanErrorMiddleware(MiddlewareMixin):
    """
    Middleware to provide cleaner error handling during development
    """

    def process_exception(self, request, exception):
        """
        Log exceptions in a cleaner format
        """
        # Don't interfere with broken pipe handling
        if isinstance(exception, (BrokenPipeError, ConnectionResetError)):
            return None

        # Log other exceptions with request context
        if hasattr(request, 'user') and request.user.is_authenticated:
            user_info = f"User: {request.user.username}"
        else:
            user_info = "User: Anonymous"

        logger.error(
            f"Exception in {request.method} {request.path} | "
            f"{user_info} | "
            f"Exception: {type(exception).__name__}: {exception}"
        )

        # Let Django handle the exception normally
        return None
