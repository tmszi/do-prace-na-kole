# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2017-03-29 16:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dpnk', '0054_auto_20170323_1621'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='variable_symbol',
            field=models.CharField(blank=True, help_text='Variable symbol of the invoice', max_length=255, null=True, unique=True, verbose_name='Variable symbol'),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='invoice_sequence_number_first',
            field=models.PositiveIntegerField(default=1, verbose_name='První číslo řady pro faktury'),
        ),
    ]