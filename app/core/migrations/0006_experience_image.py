# Generated by Django 3.2.4 on 2021-06-23 13:04

import core.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_experience'),
    ]

    operations = [
        migrations.AddField(
            model_name='experience',
            name='image',
            field=models.ImageField(null=True, upload_to=core.models.experience_image_file_path),
        ),
    ]