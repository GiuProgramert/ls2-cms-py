# utils.py

import os

from django.core.files.storage import default_storage


import cloudinary.uploader


def mdeditor_upload_handler(filename, content):
    # Generate a unique filename
    name, ext = os.path.splitext(filename)
    filename = f"{name}_{default_storage.get_available_name(filename)}"

    # Upload the file to Cloudinary
    result = cloudinary.uploader.upload(
        content, public_id=f"mdeditor/{filename}", folder="mdeditor", overwrite=True
    )

    # Return the Cloudinary URL
    return result["url"]
