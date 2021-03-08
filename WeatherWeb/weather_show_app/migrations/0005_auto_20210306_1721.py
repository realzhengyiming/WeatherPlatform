# Generated by Django 3.1.4 on 2021-03-06 09:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('weather_show_app', '0004_weather_aqi'),
    ]

    operations = [
        migrations.CreateModel(
            name='Favourite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fav_city', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='weather_show_app.city')),
            ],
        ),
        migrations.RemoveField(
            model_name='weather',
            name='wind',
        ),
        migrations.AddField(
            model_name='weather',
            name='wind_direction',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='weather',
            name='wind_power',
            field=models.FloatField(blank=True, default=0.0),
        ),
        migrations.DeleteModel(
            name='Wind',
        ),
    ]