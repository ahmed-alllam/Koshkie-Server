#  Copyright (c) Code Written and Tested by Ahmed Emad in 31/01/2020, 17:29

# Generated by Django 3.0 on 2019-12-30 14:47

from django.db import migrations, models

import drivers


class Migration(migrations.Migration):

    dependencies = [
        ('drivers', '0004_auto_20191226_1403'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='driverreviewmodel',
            options={'ordering': ['sort']},
        ),
        migrations.RenameField(
            model_name='driverprofilemodel',
            old_name='user',
            new_name='account',
        ),
        migrations.AlterField(
            model_name='driverprofilemodel',
            name='vehicle_type',
            field=models.CharField(choices=[('c', 'car'), ('m', 'motorcycle'), ('b', 'bike')], max_length=1),
        ),
        migrations.AlterUniqueTogether(
            name='driverreviewmodel',
            unique_together={('driver', 'sort')},
        ),
        migrations.AlterField(
            model_name='driverprofilemodel',
            name='profile_photo',
            field=models.ImageField(default=None, upload_to=drivers.models.photo_upload),
            preserve_default=False,
        ),
    ]
