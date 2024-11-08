import os
import cloudinary.uploader

from django.core.files.storage import default_storage


def mdeditor_upload_handler(filename, content):
    """
    Realiza la subida de un archivo a Cloudinary.

    params:
        filename -- Nombre del archivo.
        content -- Contenido del archivo.

    return:
        URL de la imagen subida.
    """

    # Generate a unique filename
    name, ext = os.path.splitext(filename)
    filename = f"{name}_{default_storage.get_available_name(filename)}"

    # Upload the file to Cloudinary
    result = cloudinary.uploader.upload(
        content, public_id=f"mdeditor/{filename}", folder="mdeditor", overwrite=True
    )

    # Return the Cloudinary URL
    return result["url"]
