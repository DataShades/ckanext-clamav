[![Test](https://github.com/DataShades/ckanext-clamav/actions/workflows/test.yml/badge.svg)](https://github.com/DataShades/ckanext-clamav/actions/workflows/test.yml)
[![codecov](https://codecov.io/github/DataShades/ckanext-clamav/graph/badge.svg)](https://codecov.io/github/DataShades/ckanext-clamav)

# ckanext-clamav

This is a basic example that helps to scan uploaded resources for malwares with clamd library.

Note: This plugin provides a custom IUploader implementation to intercept and scan 
uploaded files. However, the implementation does not return an object, allowing the 
actual IUploader implementation to take effect. If using an actual custom uploader 
such as ckanext-s3filestore, 'clamav' needs to come earlier in the configured plugin
order.

## Versions supported and Requirements

Compatibility with core CKAN versions:

  | CKAN version   | Compatibility                                                                       |
  | -------------- |-------------------------------------------------------------------------------------|
  | 2.7            | no longer supported                                                                 |
  | 2.8            | no longer supported                                 | 
  | 2.9            | unknown (last supported v1.1.0 Python3) Must: `pip install "setuptools>=44.1.0,<71"` |
  | 2.10           | yes                                                                                 |
  | 2.11           | yes                                                                                 |

## Installation

Clamd library uses clamav tool, and you must install it into your environment, to make this extension work.

For example, to install ClamAV on Ubuntu for Local Unix Socket:

1. Install ClamAV with APT
	```
    apt-get update
    apt-get install clamav clamav-daemon -y
	```

2. Update the ClamAV signature database
	```
    systemctl stop clamav-freshclam
    freshclam
    systemctl start clamav-freshclam
	```

To install ckanext-clamav:

1. Activate your CKAN virtual environment, for example:

     `. /usr/lib/ckan/default/bin/activate`

2. Clone the source and install it on the virtualenv
	```
    git clone https://github.com/DataShades/ckanext-clamav.git
    cd ckanext-clamav
    pip install -e .
	pip install -r requirements.txt
	```

3. Add `clamav` to the `ckan.plugins` setting in your CKAN
   config file (by default the config file is located at
   `/etc/ckan/default/ckan.ini`).

4. Restart CKAN. For example if you've deployed CKAN with Apache on Ubuntu:

    `sudo service apache2 reload`


## Config settings

	# If your socket file is in different folder, you can specify it
	# (optional, default: /var/run/clamav/clamd.ctl).
	ckanext.clamav.socket_path = /your/path/to/socket.file

	# You can decide to upload unscanned files or not.
    # For example, if clamav is disabled, you won't be able to scan a file
	# (optional, default: True).
	ckanext.clamav.upload_unscanned = False

    # ClamAV connection mechanism. There are two options: `tcp` or `unix`.
    # If `tcp` selected, you must provide host:port (check next options).
    # ( optional, default: unix)
    ckanext.clamav.socket_type = unix

    # TCP/IP hostname
    ckanext.clamav.tcp.host = your.hostname.address

    # TCP/IP port
    ckanext.clamav.tcp.port = 3310

    # ClamAV connection timeout. Either `tcp` or `unix`
    # By default, there is no timeout.
    # ( optional, default: 60)
    ckanext.clamav.timeout = 120


## Developer installation

To install ckanext-clamav for development, activate your CKAN virtualenv and
do:

    git clone https://github.com/DataShades/ckanext-clamav.git
    cd ckanext-clamav
    python setup.py develop
    pip install -r dev-requirements.txt


## Tests

To run the tests, do:

    pytest --ckan-ini=test.ini


## License

[AGPL](https://www.gnu.org/licenses/agpl-3.0.en.html)
