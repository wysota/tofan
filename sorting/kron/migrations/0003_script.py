# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-08 19:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kron', '0002_project_description'),
    ]

    operations = [
        migrations.CreateModel(
            name='Script',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('pipeline', models.CharField(max_length=100)),
                ('dataset', models.CharField(max_length=100)),
            ],
        ),
    ]
