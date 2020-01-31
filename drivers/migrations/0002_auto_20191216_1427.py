#  Copyright (c) Code Written and Tested by Ahmed Emad in 31/01/2020, 17:29

# Generated by Django 3.0 on 2019-12-16 14:27

from django.db import migrations, models

import drivers.models


class Migration(migrations.Migration):
    dependencies = [
        ('drivers', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='driverreviewmodel',
            name='title',
        ),
        migrations.AddField(
            model_name='driverprofilemodel',
            name='is_busy',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='driverprofilemodel',
            name='rating',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='driverprofilemodel',
            name='profile_photo',
            field=models.ImageField(null=True, upload_to=drivers.models.photo_upload),
        ),
        migrations.AlterField(
            model_name='driverreviewmodel',
            name='time_stamp',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
