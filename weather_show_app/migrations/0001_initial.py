# Generated by Django 3.1.4 on 2021-03-02 12:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('city_name', models.CharField(max_length=50, unique=True)),
                ('city_pinyin', models.CharField(max_length=50, unique=True)),
                ('city_code', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Wind',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('wind_power', models.FloatField()),
                ('wind_direction', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Weather',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('humidity', models.FloatField()),
                ('state', models.TextField()),
                ('date', models.DateField()),
                ('update_date', models.DateField(auto_now=True)),
                ('max_temperature', models.FloatField()),
                ('mini_temperature', models.FloatField()),
                ('city', models.CharField(max_length=40)),
                ('extend_detail', models.TextField()),
                ('wind', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='weather_show_app.wind')),
            ],
        ),
    ]
