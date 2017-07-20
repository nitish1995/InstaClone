# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-20 16:10
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0015_commentmodel'),
    ]

    operations = [
        migrations.AddField(
            model_name='postmodel',
            name='dirty',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='usermodel',
            name='password',
            field=models.CharField(max_length=40, validators=[django.core.validators.RegexValidator(code='min_length', message='Password should be atleast 6 character long.', regex='^.{5,}$')]),
        ),
        migrations.AlterField(
            model_name='usermodel',
            name='username',
            field=models.CharField(max_length=120, validators=[django.core.validators.RegexValidator(code='min_length', message='Usename should be atleast 4 character long.', regex='^.{4,}$')]),
        ),
    ]
