import json
import os
import re

from fastapi.templating import Jinja2Templates


def from_json(value: str):
    if not value:
        return []
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return []


def md_basico(value: str):
    if not value:
        return ""
    result = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", value)
    result = re.sub(r"`([^`]+)`", r"<code>\1</code>", result)
    return result


templates = Jinja2Templates(
    directory=os.path.join(os.path.dirname(__file__), "templates")
)

templates.env.filters["from_json"] = from_json
templates.env.filters["md_basico"] = md_basico
