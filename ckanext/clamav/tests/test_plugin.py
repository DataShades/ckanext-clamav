import os
from pathlib import Path

import pytest
import requests
from werkzeug.datastructures import FileStorage as FlaskFileStorage

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
@pytest.mark.ckan_config("ckanext.clamav.upload_unscanned", "True")
class TestUploadedUnscannedFlag:

    def test_clamav_not_called_on_upload_of_test_file(self, eicar_file_path: Path):
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
            assert "eicar.com.txt" in str(
                res,
            ), res  # provide nice message if we did not throw exception
