# Generated by Django 3.0 on 2020-01-08 20:08

from django.db import migrations, models
import shops.models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0006_auto_20191225_1814'),
        ('shops', '0013_auto_20200107_1945'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='AddOn',
            new_name='AddOnModel',
        ),
        migrations.AlterField(
            model_name='productmodel',
            name='photo',
            field=models.ImageField(null=True, upload_to=shops.models.product_photo_upload),
        ),
    ]