import socket
import sys

from clamd import ClamdNetworkSocket, ConnectionError


class CustomClamdNetworkSocket(ClamdNetworkSocket):
    """Patches the default ClamdNetworkSocket adapter
    with changed _init_socket method. The default implementation doesn't
    respect timeout properly.

    Args:
        ClamdNetworkSocket (ClamdNetworkSocket): original clamd network adapter
    """

    def _init_socket(self):
        """
        internal use only
        """
        try:
            self.clamd_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.clamd_socket.settimeout(self.timeout)
            self.clamd_socket.connect((self.host, self.port))

        except (OSError, socket.timeout):
            e = sys.exc_info()[1]
            raise ConnectionError(self._error_message(e))
