# Generated by Django 3.2.16 on 2022-12-06 15:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_profiles', '0026_alter_access_options'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='controls',
        ),
    ]
