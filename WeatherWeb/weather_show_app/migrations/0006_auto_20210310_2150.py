# Generated by Django 3.1.4 on 2021-03-10 13:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('weather_show_app', '0005_auto_20210310_2143'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dateweather',
            name='city',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='City', to='weather_show_app.city'),
        ),
    ]