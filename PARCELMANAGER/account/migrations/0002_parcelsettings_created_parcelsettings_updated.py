# Generated by Django 4.1.4 on 2022-12-29 00:31

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='parcelsettings',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='DATETIME CREATED'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='parcelsettings',
            name='updated',
            field=models.DateTimeField(auto_now=True, verbose_name='DATETIME UPDATED'),
        ),
    ]
