import os
import django
import pydoc

os.environ["DJANGO_SETTINGS_MODULE"] = "cms_py.settings"
django.setup()


pydoc.cli()
