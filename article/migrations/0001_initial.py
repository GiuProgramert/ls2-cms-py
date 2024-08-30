# Generated by Django 5.0.7 on 2024-08-30 01:53

import article.models
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('type', models.CharField(choices=[('free', 'Free'), ('suscription', 'Suscripción'), ('pay', 'Pago')], default=article.models.ArticleType['FREE'])),
                ('state', models.BooleanField(default=True)),
                ('is_moderated', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('views_number', models.IntegerField(default=0)),
                ('shares_number', models.IntegerField(default=0)),
                ('likes_number', models.IntegerField(default=0)),
                ('dislikes_number', models.IntegerField(default=0)),
                ('autor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='article.category')),
            ],
        ),
    ]
