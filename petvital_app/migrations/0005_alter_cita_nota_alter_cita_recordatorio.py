# Generated by Django 5.1.1 on 2025-06-10 00:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('petvital_app', '0004_mascota_unidad_tiempo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cita',
            name='nota',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='cita',
            name='recordatorio',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
