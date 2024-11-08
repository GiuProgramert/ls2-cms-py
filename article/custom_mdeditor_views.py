# custom_mdeditor_views.py

from mdeditor import views as mdeditor_views
from django.conf import settings
from article.utils import mdeditor_upload_handler
import json


class CustomUploadView(mdeditor_views.UploadView):
    """
    Vista personalizada para manejar las subidas de imágenes en el editor de Markdown.

    Esta vista extiende la vista UploadView predeterminada de mdeditor_views para manejar
    las subidas de imágenes específicamente para el editor de Markdown. Anula el método
    post para procesar la imagen cargada y actualizar la respuesta con la URL de la imagen
    cargada.

    Methods:
        post(request, *args, **kwargs): Maneja la subida de imágenes, procesa la imagen
    """
    def post(self, request, *args, **kwargs):
        upload_image = request.FILES.get("editormd-image-file", None)
        if upload_image:
            url = mdeditor_upload_handler(upload_image.name, upload_image.read())

            response = super().post(request, *args, **kwargs)

            data = json.loads(response._container[0].decode())
            data["url"] = url
            response._container = [json.dumps(data).encode()]

            return response

        return response
