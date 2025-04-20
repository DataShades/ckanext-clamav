from __future__ import annotations

from ckan import types
from ckan.logic.schema import validator_args


@validator_args
def clamav_scan_file(not_empty, int_validator, clamav_file_validator) -> types.Schema:
    return {
        "upload": [not_empty, clamav_file_validator],
        "size": [not_empty, int_validator],
    }
