# Generated by Django 5.0.7 on 2024-09-03 15:27

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("article", "0002_article_description_articlecontent"),
    ]

    operations = [
        migrations.AlterField(
            model_name="article",
            name="description",
            field=models.TextField(max_length=300, null=True),
        ),
    ]