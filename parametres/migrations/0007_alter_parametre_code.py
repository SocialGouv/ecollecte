# Generated by Django 3.2.13 on 2022-06-28 07:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parametres', '0006_parametre_is_deleted'),
    ]

    operations = [
        migrations.AlterField(
            model_name='parametre',
            name='code',
            field=models.CharField(help_text='LIEN_FOOTER, LOGO_FOOTER, ENTITY_PICTURE, SUPPORT_EMAIL', max_length=255, verbose_name='code'),
        ),
    ]
