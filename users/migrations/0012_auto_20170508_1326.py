# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-05-08 10:26
from __future__ import unicode_literals

from django.db import migrations, models
import utils


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0011_auto_20170508_1319'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='avatar',
            field=models.ImageField(upload_to=utils.get_file_path),
        ),
    ]