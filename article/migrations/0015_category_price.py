# Generated by Django 5.0.7 on 2024-10-06 19:03

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("article", "0014_articlestopublish"),
    ]

    operations = [
        migrations.AddField(
            model_name="category",
            name="price",
            field=models.FloatField(default=0.0, null=True),
        ),
    ]