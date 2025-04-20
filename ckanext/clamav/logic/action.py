from __future__ import annotations

from typing import Any
from datetime import datetime as dt, timezone
from datetime import timedelta as td

import jwt

import ckan.plugins.toolkit as tk
from ckan.logic import validate
from ckan.types import Context, DataDict

from ckanext.clamav import utils
from ckanext.clamav.logic import schema

TOKEN_TTL = 3600  # 1 hour


@validate(schema.clamav_scan_file)
def clamav_scan_file(context: Context, data_dict: DataDict) -> dict[str, Any]:
    # TODO: add a config option to set the max file size
    if data_dict["size"] > 1024 * 1024 * 600:  # 600MB
        raise tk.ValidationError({"upload": ["File is too large"]})

    try:
        utils.scan_file_for_viruses(data_dict)
    except tk.ValidationError as e:
        return {
            "success": False,
            "error": _format_error(e),
            "token": _create_jwt_token(data_dict, safe=False),
        }
    except ConnectionResetError:
        return {"success": False, "error": "ClamAV is not available"}

    return {"success": True, "token": _create_jwt_token(data_dict)}


def _format_error(e: tk.ValidationError) -> str:
    # TODO: can we just use e.error_summary?
    if "Virus checker" in e.error_dict:
        return e.error_dict.get("Virus checker", [""])[0]  # type: ignore

    return str(e)


def _create_jwt_token(data_dict: DataDict, safe: bool = True) -> str:
    """
    Create a JWT token that will be used to verify, that the file has been scanned
    """
    now = dt.now(timezone.utc)

    return jwt.encode(
        {
            "name": data_dict["upload"].filename,
            "size": data_dict["size"],
            "safe": safe,
            "exp": now + td(seconds=TOKEN_TTL),
            "created_at": now.timestamp(),
        },
        utils.get_secret(True),
        algorithm="HS256",
    )
