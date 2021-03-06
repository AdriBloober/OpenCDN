"""
open_cdn.server
~~~~~~~~~~~~

This module implements the api downloading in deleting.
:copyright: (c) 2020 by AdriBloober.
:license: GNU General Public License v3.0
"""

from io import BytesIO
from os.path import exists

from flask import send_file, request, jsonify

from resources.api.authentication import parse_authentication, delete_file
from resources.api.encryption import hash_key, decrypt
from resources.api.errors import FileDoesNotExists
from resources.app import app
from resources.config import config


@app.flask.route("/<string:key>/<string:filename>", methods=["GET", "DELETE"])
def download(key: str, filename: str):
    """The flask download method for downloading and deleting.
    Downloading: (GET)
    ============
    Requires: /<key>/<filename>
            key: The decrypting key and identifier for the file.
            filename: The name of the file.
    Errors: :class:`FileDoesNotExists`.
    Return: error or the file.

    Deleting: (DELETE)
    ============
    Requires: /<key>/<filename>
            key: The decrypting key and identifier for the file.
            filename: The name of the file.
            And the private_key of the file.
    Errors: :class:`FileDoesNotExists`, :class:`AccessDenied`.
    Return: error or success json.
    """
    if "/" in key or "/" in filename or ".." in key or ".." in filename:
        raise FileDoesNotExists()
    hashed_key = hash_key(key)
    filepath = f"{config.DATA_DIRECTORY}{hashed_key}/{filename}"
    if not exists(filepath):
        raise FileDoesNotExists()
    if request.method == "GET":
        with open(filepath, "rb") as file:
            content = file.read()
        decrypted_content = decrypt(content, key)
        file = BytesIO()
        file.write(decrypted_content)
        file.seek(0)
        return send_file(file, attachment_filename=filename)
    elif request.method == "DELETE":
        parse_authentication(key, filename)
        delete_file(key, filename)
        return jsonify({"status": "success"})
