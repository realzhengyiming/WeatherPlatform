# Generated by Django 3.1.4 on 2021-03-28 03:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('weather_show_app', '0015_auto_20210327_1948'),
    ]

    operations = [
        migrations.AlterField(
            model_name='city',
            name='direct_city_name',
            field=models.CharField(default='', max_length=100),
        ),
    ]