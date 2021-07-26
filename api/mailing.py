import json
import os
import sys
from typing import Dict, Optional

import requests

from api.errors import ApiError, api_error

mailjet_id = os.environ["MAILJET_ID"]
mailjet_secret = os.environ["MAILJET_SECRET"]

mjml_id = os.environ["MJML_ID"]
mjml_secret = os.environ["MJML_SECRET"]

Vars = Dict[str, str]

try:
    PYTHONPATH = os.environ["PYTHONPATH"].split(":")[0]
except KeyError as e:
    sys.exit(f"{e} not set!")

_MAILS_PATH = PYTHONPATH + "/mails/mails"


def _render_template(relative_path: str) -> str:
    """Using MJML API renders _MAILS_PATH + relative_path
       to pure HTML for later usage."""

    templates = []
    try:
        templates = os.listdir(".mails_cache")
    except FileNotFoundError:
        os.mkdir(".mails_cache")

    cached_filename = relative_path.split("/")[1] + ".html"
    if cached_filename in templates:
        print(f"Cache hit on {cached_filename}")
        with open(f".mails_cache/{cached_filename}", "r", encoding="utf-8") as f:
            return f.read()

    print(f"Cache miss on {cached_filename}")

    relative_path = _MAILS_PATH + relative_path
    with open(relative_path, encoding="utf-8") as file:
        r = requests.post(
            "https://api.mjml.io/v1/render",
            data=json.dumps({"mjml": file.read()}),
            auth=(mjml_id, mjml_secret),
        )
        if r.status_code != 200:
            raise RuntimeError(f"Error while rendering MJML template: {relative_path}")
    rendered_template = r.json()["html"]
    with open(f".mails_cache/{cached_filename}", "w", encoding="utf-8") as f:
        f.write(rendered_template)
    return rendered_template


RESET_PASSWORD = _render_template("/reset_password/reset_password.mjml")
REGISTER = _render_template("/register/register.mjml")
PASSWORD_CHANGED = _render_template("/password_changed/password_changed.mjml")
ACCOUNT_BLOCKED = _render_template("/account_blocked/account_blocked.mjml")
ACCOUNT_ACTIVATED = _render_template("/account_activated/account_activated.mjml")
ACCOUNT_DELETED = _render_template("/account_deleted/account_deleted.mjml")


def send_mail(
    to: str, subject: str, template: str, variables: Vars = None
) -> Optional[ApiError]:

    email_data = {
        "FromEmail": "preexam.rejestracja@gmail.com",
        "FromName": "PreExam",
        "Subject": subject,
        "Html-part": template,
        "Vars": variables,
        "Recipients": [{"Email": to,}],
    }

    text = json.dumps(email_data, ensure_ascii=False)
    r = requests.post(
        "https://api.mailjet.com/v3/send",
        auth=(mailjet_id, mailjet_secret),
        data=text.encode("utf-8"),
        headers={"Content-Type": "application/json; charset=utf-8"},
    )

    if r.status_code != 200:
        return api_error("email_api_error")
    return None
