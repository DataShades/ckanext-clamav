import logging
from typing import Any, Optional, Union

from clamd import BufferTooLongError, ClamdNetworkSocket, ClamdUnixSocket
from clamd import ConnectionError as ClamConnectionError
from werkzeug.datastructures import FileStorage

from ckan import logic
from ckan import model
from ckan.exceptions import CkanConfigurationException
from ckan.types import ErrorDict

from . import config as c
from .adapters import CustomClamdNetworkSocket
from .config import ClamAvStatus

log = logging.getLogger(__name__)


def scan_file_for_viruses(data_dict: dict[str, Any]) -> None:
    """
    Scans upload file for malwares with `clamav` open-source anti-virus toolkit

    Args:
        data_dict (dict[str, Any]): upload resource data_dict

    Raises:
        logic.ValidationError: returns a validation error to the user
        upload form
    """
    upload_unscanned: bool = c.upload_unscanned()

    file: FileStorage = data_dict["upload"]
    status: str
    signature: Optional[str]
    status, signature = _scan_filestream(file)
    package_id = _get_package_id(data_dict)

    if status == ClamAvStatus.ERR_DISABLE:
        log.info("Clamd: unable to connect to clamav. Can't scan the file")
        if upload_unscanned:
            log.info(_get_unscanned_file_message(file, package_id))
        else:
            raise logic.ValidationError(
                {
                    "Virus checker": [
                        "The clamav is disabled. Can't upload the file. "
                        "Contact administrator",
                    ],
                },
            )
    elif status in (ClamAvStatus.ERR_FILELIMIT,):
        log.warning(signature)
        if upload_unscanned:
            log.info(_get_unscanned_file_message(file, package_id))
        else:
            err: ErrorDict = {"Virus checker": [f"{signature}"]}
            raise logic.ValidationError(err)
    elif status == ClamAvStatus.FOUND:
        error_msg: str = (
            "malware has been found. "
            f"Filename: {file.filename}, signature: {signature}."
        )
        log.warning(error_msg)
        err: ErrorDict = {"Virus checker": [error_msg]}
        raise logic.ValidationError(err)


def _get_package_id(data_dict: dict[str, Any]) -> str:
    """In some cases, like when we are syndicating datasets with resource files,
    we are missing `package_id` from the data_dict. We are going to fetch it
    from the resource.

    If resource is is not here for some reason, just return a placeholder, because
    we are using it only for logging"""

    resource_id: Union[str, None] = data_dict.get("id")

    if not resource_id:
        return "<PACKAGE IS NOT CREATED>"
    resource = model.Resource.get(resource_id)
    if resource is None:
        return f"<PACKAGE IS NOT CREATED: resource_id: {resource_id}>"
    return resource.package.id


def _scan_filestream(file: FileStorage) -> tuple[str, Optional[str]]:
    """Scan a file stream for malware using ClamAV.

    Args:
        file (FileStorage): werkzeug FileStorage object containing the file to scan

    Returns:
        A tuple containing:
            - status_code (str): The scan status code
            - signature (Optional[str]): If malware found, contains the its signature.
                If an error occurred, contains the error message.
                If no malware found, is None.
    """

    cd: Union[ClamdUnixSocket, ClamdNetworkSocket] = _get_conn()

    try:
        scan_result: Union[dict[str, tuple[str, Optional[str]]], None] = cd.instream(
            file.stream,
        )
    except BufferTooLongError:
        error_msg: str = (
            "The uploaded file exceeds the filesize limit. "
            "The file will not be scanned"
        )
        log.error(error_msg)
        return (ClamAvStatus.ERR_FILELIMIT, error_msg)
    except ClamConnectionError:
        error_msg: str = "clamav is not accessible, check its status."
        log.critical(error_msg)
        return (ClamAvStatus.ERR_DISABLE, error_msg)

    if not scan_result:
        return (ClamAvStatus.ERR_DISABLE, None)

    return scan_result["stream"]


def _get_conn() -> Union[ClamdUnixSocket, CustomClamdNetworkSocket]:
    """
    Simply connects to the ClamAV via TCP/IP or Unix socket and returns
    the connection object

    Returns:
        Union[ClamdUnixSocket, CustomClamdNetworkSocket]: a connection to ClamAV
        Support two type of connection mechanism - TCP/IP or Unix socket

    Raises:
        CkanConfigurationException: if the TCP/IP connection mechanism has been choosen,
        the host:port must be provided, otherwise, raises an exception

        CkanConfigurationException: raises an exception, if the unsupported connection
        mechanism has been choosen
    """
    conn_timeout: int = c.conn_timeout()

    if c.socket_type() == c.SocketTypes.UNIX:
        socket_path: str = c.socket_path()
        return ClamdUnixSocket(socket_path, conn_timeout)
    tcp_host: str = c.tcp_host()
    tcp_port = c.tcp_port()

    if not tcp_port or not tcp_host:
        raise CkanConfigurationException(
            f"Clamd: please, provide TCP/IP host:port for ClamAV "
            f"received host: '{tcp_host}', port: '{tcp_port}'",
        )

    return CustomClamdNetworkSocket(tcp_host, tcp_port, conn_timeout)


def _get_unscanned_file_message(file: FileStorage, pkg_id: str) -> str:
    return (
        "The unscanned file will be uploaded because unscanned fileupload is enabled. "
        f"File: {file.filename}, pkg: {pkg_id}, name: {file.filename or None}"
    )
