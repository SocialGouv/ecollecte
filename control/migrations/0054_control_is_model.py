# Generated by Django 4.2.1 on 2024-11-28 11:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('control', '0053_alter_questionnairefile_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='control',
            name='is_model',
            field=models.BooleanField(default=False, help_text='Indique si cette procédure est un modèle', verbose_name='Modèle'),
        ),
    ]
