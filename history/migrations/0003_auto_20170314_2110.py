# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-14 21:10
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('history', '0002_rename_model_field'),
    ]

    operations = [
        migrations.AlterIndexTogether(
            name='modelhistory',
            index_together=set([('app_label', 'model_name')]),
        ),
    ]
