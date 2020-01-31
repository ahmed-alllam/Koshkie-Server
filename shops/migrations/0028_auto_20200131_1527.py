#  Copyright (c) Code Written and Tested by Ahmed Emad in 31/01/2020, 17:29

# Generated by Django 3.0 on 2020-01-31 15:27

from django.db import migrations, models

import shops.models


class Migration(migrations.Migration):
    dependencies = [
        ('shops', '0027_auto_20200131_1427'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shopprofilemodel',
            name='profile_photo',
            field=models.ImageField(default=None, upload_to=shops.models.shop_photo_upload),
            preserve_default=False,
        ),
    ]
