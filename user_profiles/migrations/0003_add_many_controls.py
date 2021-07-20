# Generated by Django 2.1.7 on 2019-03-07 11:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('control', '0020_optional_questionnaire_file'),
        ('user_profiles', '0002_userprofile_send_files_report'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='controls',
            field=models.ManyToManyField(blank=True, related_name='user_profiles', to='control.Control', verbose_name='controles'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='control',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='control.Control', verbose_name='controle'),
        ),
    ]
