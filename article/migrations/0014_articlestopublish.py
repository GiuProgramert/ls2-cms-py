# Generated by Django 5.0.7 on 2024-10-06 17:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("article", "0013_article_published_at"),
    ]

    operations = [
        migrations.CreateModel(
            name="ArticlesToPublish",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("to_publish_at", models.DateTimeField()),
                ("published", models.BooleanField(default=False)),
                (
                    "article",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="article.article",
                    ),
                ),
            ],
        ),
    ]
