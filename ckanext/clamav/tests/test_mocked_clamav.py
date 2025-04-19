from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import requests
from clamd import BufferTooLongError, ConnectionError
from werkzeug.datastructures import FileStorage as FlaskFileStorage

import ckan.plugins.toolkit as tk
from ckan.tests import factories, helpers

clean_string = b"safe file content"
EICAR_URL = "https://secure.eicar.org/eicar.com.txt"
EICAR_LOCAL_PATH = Path("tests/eicar.com.txt")


@pytest.fixture(scope="session")
def eicar_file_path():
    EICAR_LOCAL_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not EICAR_LOCAL_PATH.exists():
        response = requests.get(EICAR_URL)
        response.raise_for_status()
        with open(EICAR_LOCAL_PATH, "wb") as f:
            f.write(response.content)
    return EICAR_LOCAL_PATH


@pytest.mark.usefixtures("clean_db", "clean_index", "with_plugins")
@pytest.mark.ckan_config("ckan.plugins", "clamav")
@pytest.mark.ckan_config("ckanext.clamav.socket_type", "unix")
@pytest.mark.ckan_config("ckanext.clamav.socket_path", "/this/is/mocked")
class TestMockClamAVLimitTesting:

    @pytest.mark.ckan_config("ckanext.clamav.upload_unscanned", "False")
    def test_clamav_hit_file_limit_error_throw_validation_error(
        self, eicar_file_path: Path,
    ):
        with patch("ckanext.clamav.utils.ClamdUnixSocket") as mock_unix_socket:
            # Make the instance that gets returned by ClamdUnixSocket()
            mock_clamd = MagicMock()
            mock_unix_socket.return_value = mock_clamd
            mock_clamd.instream.side_effect = BufferTooLongError()

            user = factories.Sysadmin()
            dataset = factories.Dataset(user=user)

            with open(eicar_file_path, "rb") as f:
                with pytest.raises(tk.ValidationError) as excinfo:
                    res = helpers.call_action(
                        "resource_create",
                        context={"user": user["name"], "ignore_auth": False},
                        package_id=dataset["id"],
                        url="",
                        upload=FlaskFileStorage(
                            stream=f,
                            filename="eicar.com.txt",
                            content_type="text/plain",
                        ),
                        name="Infected File",
                    )
                    pytest.fail(
                        f"Was not blocked:{res}",
                    )  # provide nice message if we did not throw exception

                # Verify Rate limit error was thrown
                assert (
                    "{'Virus checker': ['The uploaded file exceeds the filesize limit. "
                    "The file will not be scanned']}" in str(excinfo.value)
                ), str(excinfo.value)

    @pytest.mark.ckan_config("ckanext.clamav.upload_unscanned", "True")
    def test_clamav_hit_file_limit_error_allow_unscanned(self, eicar_file_path: Path):
        with patch("ckanext.clamav.utils.ClamdUnixSocket") as mock_unix_socket:
            # Make the instance that gets returned by ClamdUnixSocket()
            mock_clamd = MagicMock()
            mock_unix_socket.return_value = mock_clamd

            mock_clamd.instream.side_effect = BufferTooLongError()

            user = factories.Sysadmin()
            dataset = factories.Dataset(user=user)

            with open(eicar_file_path, "rb") as f:

                res = helpers.call_action(
                    "resource_create",
                    context={"user": user["name"], "ignore_auth": False},
                    package_id=dataset["id"],
                    url="",
                    upload=FlaskFileStorage(
                        stream=f,
                        filename="eicar.com.txt",
                        content_type="text/plain",
                    ),
                    name="Infected File",
                )
                assert "id" in res, "Resource was not created successfully:" + res

    @pytest.mark.ckan_config("ckanext.clamav.upload_unscanned", "True")
    def test_clamav_connection_error_allow_unscanned(self, eicar_file_path: Path):
        with patch("ckanext.clamav.utils.ClamdUnixSocket") as mock_unix_socket:
            # Make the instance that gets returned by ClamdUnixSocket()
            mock_clamd = MagicMock()
            mock_unix_socket.return_value = mock_clamd

            mock_clamd.instream.side_effect = ConnectionError()

            user = factories.Sysadmin()
            dataset = factories.Dataset(user=user)

            with open(eicar_file_path, "rb") as f:

                res = helpers.call_action(
                    "resource_create",
                    context={"user": user["name"], "ignore_auth": False},
                    package_id=dataset["id"],
                    url="",
                    upload=FlaskFileStorage(
                        stream=f,
                        filename="eicar.com.txt",
                        content_type="text/plain",
                    ),
                    name="Infected File",
                )
                assert "id" in res, "Resource was not created successfully:" + res
