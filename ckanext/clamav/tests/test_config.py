import pytest

from ckan.exceptions import CkanConfigurationException

import ckanext.clamav.config as c


class TestClamAVConfig:

    def test_config_defaults(self):
        assert c.upload_unscanned()
        assert c.socket_type() == "unix"
        assert c.socket_path() == "/var/run/clamav/clamd.ctl"
        assert c.conn_timeout() == 60
        assert c.tcp_host() is None
        assert c.tcp_host() is None

    @pytest.mark.ckan_config("ckanext.clamav.socket_path", "/tmp/socket")
    def test_config_overrides_socket_path(self):
        assert c.socket_path() == "/tmp/socket"

    @pytest.mark.ckan_config("ckanext.clamav.timeout", "10")
    def test_config_overrides_timeout(self):
        assert c.conn_timeout() == 10

    @pytest.mark.ckan_config("ckanext.clamav.upload_unscanned", "False")
    def test_config_overrides_unscanned(self):
        assert c.upload_unscanned() is False

    @pytest.mark.ckan_config("ckanext.clamav.tcp.host", "/abc")
    def test_config_overrides_tcp_host(self):
        assert c.tcp_host() == "/abc"

    @pytest.mark.ckan_config("ckanext.clamav.tcp.port", 80)
    def test_config_overrides_tcp_port(self):
        assert c.tcp_port() == 80

    @pytest.mark.ckan_config("ckanext.clamav.socket_type", "tcp")
    def test_config_overrides_sockt_type(self):
        assert c.socket_type() == "tcp"

    @pytest.mark.ckan_config("ckanext.clamav.socket_type", "invalid")
    def test_config_overrides_sockt_type_invalid(self):
        with pytest.raises(CkanConfigurationException) as excinfo:
            c.socket_type()
            pytest.fail(
                "Exception not thrown on invalid socket type",
            )  # provide nice message if we did not throw exception

        # Verify Exception message
        assert "Clamd: unsupported connection type" in str(excinfo.value), str(
            excinfo.value,
        )
