# Generated by Django 3.1.4 on 2021-03-26 12:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('weather_show_app', '0012_auto_20210325_2227'),
    ]

    operations = [
        migrations.AddField(
            model_name='dateweather',
            name='dressing_index_desc',
            field=models.TextField(default=''),
        ),
    ]
