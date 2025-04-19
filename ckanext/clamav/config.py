from typing import Optional
import ckantoolkit as tk

from ckan.exceptions import CkanConfigurationException


class SocketTypes:
    # could be Enum but keeping it system for now
    UNIX = u'unix'
    TCP = u'tcp'


class ClamAvStatus:
    # could be Enum but keeping it system for now
    FOUND = u'FOUND'
    ERR_FILELIMIT = u'ERR_FILELIMIT'
    ERR_DISABLE = u'ERR_DISABLED'


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
    """ ckanext.clamav.socket_path defaults to True"""
    return tk.asbool(  # type: ignore[attr-defined]
        tk.config.get(CLAMAV_CONF_UPLOAD_UNSCANNED, CLAMAV_CONF_UPLOAD_UNSCANNED_DF)  # type: ignore[attr-defined]
    )


def socket_type() -> str:
    """ ckanext.clamav.socket_type defaults to UNIX"""
    socket_type_val = tk.config.get(CLAMAV_CONF_SOCKET_TYPE, CLAMAV_CONF_SOCKET_TYPE_DF)  # type: ignore[attr-defined]
    if socket_type_val not in (SocketTypes.UNIX, SocketTypes.TCP):
        raise CkanConfigurationException("Clamd: unsupported connection type")

    return socket_type_val


def conn_timeout() -> int:
    """ ckanext.clamav.timeout defaults to 60"""
    return tk.asint(tk.config.get(CLAMAV_CONF_CONN_TIMEOUT, CLAMAV_CONF_CONN_TIMEOUT_DF))  # type: ignore[attr-defined]


def socket_path() -> str:
    """ ckanext.clamav.socket_path defaults to /var/run/clamav/clamd.ctl"""
    return tk.config.get(CLAMAV_CONF_SOCKET_PATH, CLAMAV_CONF_SOCKET_PATH_DF)  # type: ignore[attr-defined]


def tcp_host() -> str:
    """ ckanext.clamav.tcp_host no default"""
    return tk.config.get(CLAMAV_CONF_SOCK_TCP_HOST)  # type: ignore[attr-defined]


def tcp_port() -> Optional[int]:
    """ ckanext.clamav.tcp_host no default"""
    if tk.config.get(CLAMAV_CONF_SOCK_TCP_PORT):  # type: ignore[attr-defined]
        return tk.asint(tk.config.get(CLAMAV_CONF_SOCK_TCP_PORT))  # type: ignore[attr-defined]
    return None
