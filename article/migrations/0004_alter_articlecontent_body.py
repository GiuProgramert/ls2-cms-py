# Generated by Django 5.0.7 on 2024-09-09 23:38

import mdeditor.fields
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("article", "0003_alter_article_description"),
    ]

    operations = [
        migrations.AlterField(
            model_name="articlecontent",
            name="body",
            field=mdeditor.fields.MDTextField(),
        ),
    ]