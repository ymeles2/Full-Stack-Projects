# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-24 00:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('taxonomy', '0004_producttaxonomy'),
    ]

    operations = [
        migrations.AddField(
            model_name='producttaxonomy',
            name='breadcrumb',
            field=models.CharField(blank=True, editable=False, max_length=9999, null=True),
        ),
        migrations.AddField(
            model_name='producttaxonomy',
            name='level_0',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='producttaxonomy',
            name='level_1',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='producttaxonomy',
            name='lineage_slugs',
            field=models.SlugField(blank=True, editable=False, max_length=256, null=True),
        ),
    ]
