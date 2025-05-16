from __future__ import annotations

from typing import Any, Optional

import ckan.plugins as p
from ckan.plugins import toolkit
from ckan.common import CKANConfig

from . import utils


class ClamavPlugin(p.SingletonPlugin):
    p.implements(p.IConfigurer)
    p.implements(p.IUploader, inherit=True)

    # IConfigurer

    def update_config(self, config: "CKANConfig"):
        toolkit.add_template_directory(config, "templates")
        toolkit.add_public_directory(config, "public")
        toolkit.add_resource("fanstatic", "clamav")

    # IUploader

    def get_resource_uploader(self, data_dict: dict[str, Any]):
        if not data_dict.get("upload"):
            return

        utils.scan_file_for_viruses(data_dict)

    def get_uploader(self, upload_to: str, old_filename: Optional[str]):
        return
