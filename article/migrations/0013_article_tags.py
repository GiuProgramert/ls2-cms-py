# Generated by Django 5.0.7 on 2024-10-06 21:37

import taggit.managers
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("article", "0012_alter_article_state"),
        (
            "taggit",
            "0006_rename_taggeditem_content_type_object_id_taggit_tagg_content_8fc721_idx",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="article",
            name="tags",
            field=taggit.managers.TaggableManager(
                help_text="A comma-separated list of tags.",
                through="taggit.TaggedItem",
                to="taggit.Tag",
                verbose_name="Tags",
            ),
        ),
    ]
