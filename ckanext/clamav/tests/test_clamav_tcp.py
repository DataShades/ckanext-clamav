import os
from io import BytesIO

import requests
import pytest
from pathlib import Path
import ckantoolkit as tk

from ckan.exceptions import CkanConfigurationException
from ckan.tests import helpers, factories
from werkzeug.datastructures import FileStorage as FlaskFileStorage

clean_string = b"safe file content"
EICAR_URL = "https://secure.eicar.org/eicar.com.txt"
EICAR_LOCAL_PATH = Path("tests/eicar.com.txt")

# This is to allow localhost testing or container testing by setting CLAMAV_HOST, default localhost
clamav_host = os.environ.get('CLAMAV_HOST', 'localhost')
clamav_port = os.environ.get('CLAMAV_PORT', '3310')
clamav_socket = os.environ.get('CLAMAV_SOCKET', '/var/run/clamav/clamd.ctl')


@pytest.fixture(scope="session")
def eicar_file_path():
    EICAR_LOCAL_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not EICAR_LOCAL_PATH.exists():
        response = requests.get(EICAR_URL)
        response.raise_for_status()
        with open(EICAR_LOCAL_PATH, "wb") as f:
            f.write(response.content)
    return EICAR_LOCAL_PATH


def create_file(data, filename):
    test_file = BytesIO()
    if isinstance(data, str):
        data = bytes(data, encoding="utf-8")
    test_file.write(data)
    test_file.seek(0)
    return FlaskFileStorage(test_file, filename)


@pytest.mark.usefixtures(u"clean_db", u"clean_index", u'with_plugins')
@pytest.mark.ckan_config("ckan.plugins", "clamav")
@pytest.mark.ckan_config("ckanext.clamav.upload_unscanned", "False")
@pytest.mark.ckan_config("ckanext.clamav.socket_type", "tcp")
class TestClamAvTcpAgentMisconfiguration:

    @pytest.mark.ckan_config("ckanext.clamav.tcp.port", clamav_port)
    def test_clamav_missing_tcp_host(self):
        user = factories.Sysadmin()
        dataset = factories.Dataset(user=user)
        with pytest.raises(CkanConfigurationException):
            helpers.call_action(
                "resource_create",
                context={"user": user["name"], "ignore_auth": False},
                package_id=dataset["id"],
                url="",
                upload=create_file(clean_string, 'safe.txt'),
                name="Clean File",
            )
            pytest.fail("Should have thrown configuration exception")

    @pytest.mark.ckan_config("ckanext.clamav.tcp.host", clamav_host)
    def test_clamav_missing_tcp_port(self):
        user = factories.Sysadmin()
        dataset = factories.Dataset(user=user)

        with pytest.raises(CkanConfigurationException):
            helpers.call_action(
                "resource_create",
                context={"user": user["name"], "ignore_auth": False},
                package_id=dataset["id"],
                url="",
                upload=create_file(clean_string, 'safe.txt'),
                name="Clean File",
            )
            pytest.fail("Should have thrown configuration exception")


@pytest.mark.usefixtures(u"clean_db", u"clean_index", u'with_plugins')
@pytest.mark.ckan_config("ckan.plugins", "clamav")
@pytest.mark.ckan_config("ckanext.clamav.upload_unscanned", "False")
@pytest.mark.ckan_config("ckanext.clamav.socket_type", "tcp")
@pytest.mark.ckan_config("ckanext.clamav.tcp.host", clamav_host)
@pytest.mark.ckan_config("ckanext.clamav.tcp.port", clamav_port)
class TestClamAvTcpAgent:

    def test_clamav_allows_clean_file_via_tcp_clamd(self):
        user = factories.Sysadmin()
        dataset = factories.Dataset(user=user)

        """Test that ClamAV allows clean files."""
        res = helpers.call_action(
            "resource_create",
            context={"user": user["name"], "ignore_auth": False},
            package_id=dataset["id"],
            url="",
            upload=create_file(clean_string, 'safe.txt'),
            name="Clean File",
        )

        # Check if the resource was created
        assert "id" in res, "Resource was not created successfully:" + res

    def test_clamav_blocks_infected_file_via_tcp_clamd(self, eicar_file_path):
        user = factories.Sysadmin()
        dataset = factories.Dataset(user=user)

        with open(eicar_file_path, "rb") as f:
            """Test that ClamAV blocks infected files."""
            with pytest.raises(tk.ValidationError) as excinfo:
                res = helpers.call_action(
                    "resource_create",
                    context={"user": user["name"], "ignore_auth": False},
                    package_id=dataset["id"],
                    url="",
                    upload=FlaskFileStorage(stream=f, filename="eicar.com.txt", content_type="text/plain"),
                    name="Infected File",
                )
                pytest.fail("Was not tagged as infected:{}".format(res))  # provide nice message if we did not throw exception

            # Verify ClamAV blocked the file
            assert "{'virus checker': ['malware has been found. filename: eicar.com.txt, signature: win.test.eicar_hdb-1.']}" in str(excinfo.value).lower(), str(excinfo.value).lower()
