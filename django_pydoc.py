import os
import django
import pydoc


if __name__ == "__main__":
    os.environ["DJANGO_SETTINGS_MODULE"] = "cms_py.settings"
    django.setup()

    pydoc.cli()
