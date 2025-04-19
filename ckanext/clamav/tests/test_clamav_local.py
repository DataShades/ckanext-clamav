import os
from io import BytesIO
from pathlib import Path
from typing import Union

import pytest
import requests
from werkzeug.datastructures import FileStorage as FlaskFileStorage

import ckan.plugins.toolkit as tk
from ckan.tests import factories, helpers

clean_string = b"safe file content"
EICAR_URL = "https://secure.eicar.org/eicar.com.txt"
EICAR_LOCAL_PATH = Path("tests/eicar.com.txt")

# This is to allow localhost testing or container testing by setting CLAMAV_HOST,
# default localhost
clamav_host = os.environ.get("CLAMAV_HOST", "localhost")
clamav_port = os.environ.get("CLAMAV_PORT", "3310")
clamav_socket = os.environ.get("CLAMAV_SOCKET", "/var/run/clamav/clamd.ctl")


@pytest.fixture(scope="session")
def eicar_file_path() -> Path:
    EICAR_LOCAL_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not EICAR_LOCAL_PATH.exists():
        response = requests.get(EICAR_URL)
        response.raise_for_status()
        with open(EICAR_LOCAL_PATH, "wb") as f:
            f.write(response.content)
    return EICAR_LOCAL_PATH


def create_file(data: Union[str, bytes], filename: str) -> FlaskFileStorage:
    test_file = BytesIO()
    if isinstance(data, str):
        data = bytes(data, encoding="utf-8")
    test_file.write(data)
    test_file.seek(0)
    return FlaskFileStorage(test_file, filename)


@pytest.mark.usefixtures("clean_db", "clean_index", "with_plugins")
@pytest.mark.ckan_config("ckan.plugins", "clamav")
@pytest.mark.ckan_config("ckanext.clamav.upload_unscanned", "False")
@pytest.mark.ckan_config("ckanext.clamav.socket_type", "unix")
@pytest.mark.ckan_config("ckanext.clamav.socket_path", clamav_socket)
class TestClamAvLocalDaemon:

    def test_clamav_allows_clean_file(self):
        user = factories.Sysadmin()
        dataset = factories.Dataset(user=user)

        """Test that ClamAV allows clean files."""
        res = helpers.call_action(
            "resource_create",
            context={"user": user["name"], "ignore_auth": False},
            package_id=dataset["id"],
            url="",
            upload=create_file(clean_string, "safe.txt"),
            name="Clean File",
        )

        # Check if the resource was created
        assert "id" in res, "Resource was not created successfully:" + res

    def test_clamav_blocks_infected_file(self, eicar_file_path: Path):
        user = factories.Sysadmin()
        dataset = factories.Dataset(user=user)

        with open(eicar_file_path, "rb") as f:
            """Test that ClamAV blocks infected files locally."""
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
                    f"Was not tagged as infected:{res}",
                )  # provide nice message if we did not throw exception

            # Verify ClamAV blocked the file
            assert (
                "{'virus checker': ['malware has been found. filename: eicar.com.txt, "
                "signature: win.test.eicar_hdb-1.']}" in str(excinfo.value).lower()
            ), str(excinfo.value).lower()


@pytest.mark.usefixtures("clean_db", "clean_index", "with_plugins")
@pytest.mark.ckan_config("ckan.plugins", "clamav")
class TestClamAvUnitAgentMisconfiguration:

    @pytest.mark.ckan_config("ckanext.clamav.upload_unscanned", "True")
    @pytest.mark.ckan_config("ckanext.clamav.socket_type", "unix")
    @pytest.mark.ckan_config("ckanext.clamav.socket_path", "/does/not/exist")
    def test_clamav_invalid_unix_socket_allowed_pass(self):
        user = factories.Sysadmin()
        dataset = factories.Dataset(user=user)

        """Test that ClamAV allows clean files."""
        res = helpers.call_action(
            "resource_create",
            context={"user": user["name"], "ignore_auth": False},
            package_id=dataset["id"],
            url="",
            upload=create_file(clean_string, "safe.txt"),
            name="Clean File",
        )

        # Check if the resource was created
        assert "id" in res, "Resource was not created successfully:" + res
