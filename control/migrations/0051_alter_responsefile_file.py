# Generated by Django 3.2.14 on 2022-08-01 12:41

import control.upload_path
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('control', '0050_alter_control_reference_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='responsefile',
            name='file',
            field=models.FileField(max_length=2000, upload_to=control.upload_path.response_file_path, verbose_name='fichier'),
        ),
    ]
