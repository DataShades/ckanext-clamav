from typing import Any, Optional
from datetime import datetime as dt, timezone

import jwt
import ckan.plugins as p
from ckan.plugins import toolkit
from ckan.common import CKANConfig

from ckanext.clamav import config, utils


@toolkit.blanket.actions
@toolkit.blanket.validators
class ClamavPlugin(p.SingletonPlugin):
    p.implements(p.IConfigurer)
    p.implements(p.IUploader, inherit=True)

    # IConfigurer

    def update_config(self, config: "CKANConfig"):
        toolkit.add_template_directory(config, "templates")
        toolkit.add_resource("assets", "clamav")

    # IUploader

    def get_resource_uploader(self, data_dict: dict[str, Any]):
        if not data_dict.get("upload"):
            return

        if config.upload_unscanned():
            return

        if not self._check_token(data_dict):
            raise toolkit.ValidationError(
                {"Virus checker": ["The file has not been scanned or is infected"]},
            )

    def _check_token(self, data_dict: dict[str, Any]) -> bool:
        """Check if the file has been scanned and is safe

        Args:
            data_dict: The data dictionary from the resource edit form

        Returns:
            True if the file has been scanned and is safe, False otherwise
        """
        token = data_dict.get("clamav_token", "")
        file = data_dict["upload"]

        if not token:
            return False

        try:
            token_data: dict[str, Any] = jwt.decode(
                token,
                utils.get_secret(False),
                algorithms=["HS256"],
            )
        except (jwt.ExpiredSignatureError, jwt.DecodeError):
            return False

        if not token_data.get("safe"):
            return False

        import ipdb; ipdb.set_trace()

        if (token_data.get("name") != file.filename) or (
            token_data.get("size") != file.stream.seek(0, 2)
        ):
            return False

        file.stream.seek(0)
        # checking for filename and filesize provides reasonable security without being too expensive.
        # While checking file content would be more secure, it would require re-scanning the file,
        # defeating the purpose of the token. The combination of filename and size makes it much harder
        # to substitute a malicious file while reusing a valid token.

        return dt.fromtimestamp(token_data["exp"], tz=timezone.utc) < dt.now(
            timezone.utc,
        )

    def get_uploader(self, upload_to: str, old_filename: Optional[str]):
        return
