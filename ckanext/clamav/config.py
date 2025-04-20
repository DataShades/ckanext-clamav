from typing import Optional

import ckan.plugins.toolkit as tk
from ckan.exceptions import CkanConfigurationException


class SocketTypes:
    UNIX = "unix"
    TCP = "tcp"


class ClamAvStatus:
    FOUND = "FOUND"
    ERR_FILELIMIT = "ERR_FILELIMIT"
    ERR_DISABLE = "ERR_DISABLED"


CLAMAV_CONF_SOCKET_PATH: str = "ckanext.clamav.socket_path"
CLAMAV_CONF_SOCKET_PATH_DF: str = "/var/run/clamav/clamd.ctl"
CLAMAV_CONF_UPLOAD_UNSCANNED: str = "ckanext.clamav.upload_unscanned"
CLAMAV_CONF_UPLOAD_UNSCANNED_DF: bool = True

CLAMAV_CONF_SOCKET_TYPE: str = "ckanext.clamav.socket_type"
CLAMAV_CONF_SOCKET_TYPE_DF: str = SocketTypes.UNIX
CLAMAV_CONF_SOCK_TCP_HOST: str = "ckanext.clamav.tcp.host"
CLAMAV_CONF_SOCK_TCP_PORT: str = "ckanext.clamav.tcp.port"
CLAMAV_CONF_CONN_TIMEOUT: str = "ckanext.clamav.timeout"
CLAMAV_CONF_CONN_TIMEOUT_DF: int = 60


def upload_unscanned() -> bool:
    """Get whether unscanned files should be uploaded.

    Returns:
        True if unscanned files should be uploaded, False otherwise.
        Defaults to True via ckanext.clamav.upload_unscanned config option.
    """
    return tk.asbool(
        tk.config.get(CLAMAV_CONF_UPLOAD_UNSCANNED, CLAMAV_CONF_UPLOAD_UNSCANNED_DF),
    )


def socket_type() -> str:
    """Get the socket type.

    Returns:
        The socket type.
        Defaults to UNIX via ckanext.clamav.socket_type config option.
    """
    socket_type_val = tk.config.get(CLAMAV_CONF_SOCKET_TYPE, CLAMAV_CONF_SOCKET_TYPE_DF)
    if socket_type_val not in (SocketTypes.UNIX, SocketTypes.TCP):
        raise CkanConfigurationException("Clamd: unsupported connection type")

    return socket_type_val


def conn_timeout() -> int:
    """Get the connection timeout.

    Returns:
        The connection timeout.
        Defaults to 60 via ckanext.clamav.timeout config option.
    """
    return tk.asint(
        tk.config.get(CLAMAV_CONF_CONN_TIMEOUT, CLAMAV_CONF_CONN_TIMEOUT_DF),
    )


def socket_path() -> str:
    """Get the socket path.

    Returns:
        The socket path.
        Defaults to /var/run/clamav/clamd.ctl via ckanext.clamav.socket_path
            config option.
    """
    return tk.config.get(CLAMAV_CONF_SOCKET_PATH, CLAMAV_CONF_SOCKET_PATH_DF)


def tcp_host() -> str:
    """Get the TCP host.

    Returns:
        The TCP host.
        Defaults to None via ckanext.clamav.tcp_host config option.
    """
    return tk.config.get(CLAMAV_CONF_SOCK_TCP_HOST)


def tcp_port() -> Optional[int]:
    """Get the TCP port.

    Returns:
        The TCP port.
        Defaults to None via ckanext.clamav.tcp_port config option.
    """
    if tk.config.get(CLAMAV_CONF_SOCK_TCP_PORT):
        return tk.asint(tk.config.get(CLAMAV_CONF_SOCK_TCP_PORT))
    return None
