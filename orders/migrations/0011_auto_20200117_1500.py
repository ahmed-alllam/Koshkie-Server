# Generated by Django 3.0 on 2020-01-17 15:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0010_auto_20200116_1547'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitemmodel',
            name='price',
            field=models.FloatField(default=0),
        ),
    ]