# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-20 19:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0016_auto_20170720_2140'),
    ]

    operations = [
        migrations.AddField(
            model_name='commentmodel',
            name='upvote',
            field=models.IntegerField(default=0),
        ),
    ]
