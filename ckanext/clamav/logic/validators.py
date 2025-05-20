from __future__ import annotations

from typing import Any

from werkzeug.datastructures import FileStorage

import ckan.plugins.toolkit as tk


def clamav_file_validator(value: Any) -> Any:
    if not isinstance(value, FileStorage):
        raise tk.Invalid(tk._("File is required"))

    return value
