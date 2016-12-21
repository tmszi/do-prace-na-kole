# -*- coding: utf-8 -*-
# Generated by Django 1.11.dev20161107131156 on 2016-12-19 16:21
from __future__ import unicode_literals

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('coupons', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='discountcoupon',
            name='author',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='discountcoupon_create', to=settings.AUTH_USER_MODEL, verbose_name='author'),
        ),
        migrations.AddField(
            model_name='discountcoupon',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True, verbose_name='Datum vytvoření'),
        ),
        migrations.AddField(
            model_name='discountcoupon',
            name='updated',
            field=models.DateTimeField(auto_now=True, null=True, verbose_name='Datum poslední změny'),
        ),
        migrations.AddField(
            model_name='discountcoupon',
            name='user_attendance_number',
            field=models.PositiveIntegerField(blank=True, default=1, help_text='Pokud se nevyplní, bude počet využití neomezený', null=True, verbose_name='Počet možných využití'),
        ),
        migrations.AlterField(
            model_name='discountcoupon',
            name='discount',
            field=models.PositiveIntegerField(default=100, validators=[django.core.validators.MaxValueValidator(100)], verbose_name='sleva (v procentech)'),
        ),
        migrations.AddField(
            model_name='discountcoupon',
            name='updated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='discountcoupon_update', to=settings.AUTH_USER_MODEL, verbose_name='last updated by'),
        ),
        migrations.AddField(
            model_name='discountcoupon',
            name='coupon_pdf',
            field=models.FileField(blank=True, null=True, upload_to='coupons', verbose_name='PDF kupón'),
        ),
        migrations.AddField(
            model_name='discountcoupontype',
            name='campaign',
            field=models.ForeignKey(default=7, on_delete=django.db.models.deletion.CASCADE, to='dpnk.Campaign', verbose_name='Kampaň'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='discountcoupontype',
            name='valid_until',
            field=models.DateField(blank=True, default=None, null=True, verbose_name='Platný do'),
        ),
    ]
