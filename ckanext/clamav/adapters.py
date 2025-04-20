import socket
import sys

from clamd import ClamdNetworkSocket, ConnectionError


class CustomClamdNetworkSocket(ClamdNetworkSocket):
    """Patches the default ClamdNetworkSocket adapter with proper timeout handling.

    The default ClamdNetworkSocket implementation doesn't properly respect the timeout
    setting. This class fixes that by correctly setting the socket timeout.

    Args:
        host (str): Hostname or IP address of ClamAV server
        port (int): Port number ClamAV is listening on
        timeout (float): Socket timeout in seconds
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
