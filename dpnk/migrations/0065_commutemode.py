# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-05-11 18:18
from __future__ import unicode_literals

from django.db import migrations, models

def forwards_func(apps, schema_editor):
    CommuteMode = apps.get_model("dpnk", "CommuteMode")
    db_alias = schema_editor.connection.alias
    CommuteMode.objects.using(db_alias).bulk_create([
        CommuteMode(
            id=1,
            slug='bicycle',
            name="Kolo",
            name_cs="Kolo",
            name_en="Bicycle",
            tooltip="Cesta byla vykonána na kole, koloběžce, skateboardu...\nDopravní prostředky se mohou kombinovat,\npočítá se však pouze ujetá vzdálenost.",
            tooltip_cs="Cesta byla vykonána na kole, koloběžce, skateboardu...\nDopravní prostředky se mohou kombinovat,\npočítá se však pouze ujetá vzdálenost.",
            tooltip_en="Trip was made on bicycle, kick scooter, skateboard...\n traffic modes can be combined,\nbut only ridden distanc can be filled in.",
            order=0,
        ),
        CommuteMode(
            id=2,
            slug='by_foot',
            name="Chůze/běh",
            name_cs="Chůze/běh",
            name_en="Walk/run",
            tooltip="Cesta byla vykonána pěšky, nebo během.\nPočítá se minimální vzdálenost 1,5 km.",
            tooltip_cs="Cesta byla vykonána pěšky, nebo během.\nPočítá se minimální vzdálenost 1,5 km.",
            tooltip_en="Trip was made by walking or running.\nTrip must be at least 1,5 km long.",
            order=2,
        ),
        CommuteMode(
            id=3,
            slug='by_other_vehicle',
            name="Jinak",
            name_cs="Jinak",
            name_en="Other",
            tooltip="Cesta byla vykonána autem,\nhromadnou dopravou, taxíkem...",
            tooltip_cs="Cesta byla vykonána autem,\nhromadnou dopravou, taxíkem...",
            tooltip_en="Trip was made by car,\n public transport, taxi...",
            order=3,
        ),
        CommuteMode(
            id=4,
            slug='no_work',
            name="Žádná cesta",
            name_cs="Žádná cesta",
            name_en="No trip",
            tooltip="Tato cesta nebyla vůbec vykonána.\nSoutěžící daný den tedy vůbec nepracoval,\nnebo cestu z jiného důvodu nevykonal.",
            tooltip_cs="Tato cesta nebyla vůbec vykonána.\nSoutěžící daný den tedy vůbec nepracoval,\nnebo cestu z jiného důvodu nevykonal.",
            tooltip_en="This trip was not done at all.\nCompetitor did not work that day,\n or did not make the trip for other reason.",
            does_count=False,
            order=4,
        ),
    ])

def reverse_func(apps, schema_editor):
    CommuteMode = apps.get_model("dpnk", "CommuteMode")
    db_alias = schema_editor.connection.alias
    CommuteMode.objects.using(db_alias).filter(slug='bicycle').delete()
    CommuteMode.objects.using(db_alias).filter(slug='by_foot').delete()
    CommuteMode.objects.using(db_alias).filter(slug='by_other_vehicle').delete()
    CommuteMode.objects.using(db_alias).filter(slug='no_work').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('dpnk', '0064_auto_20170510_1156'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommuteMode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=160, verbose_name='Název módu dopravy')),
                ('name_en', models.CharField(max_length=160, null=True, verbose_name='Název módu dopravy')),
                ('name_cs', models.CharField(max_length=160, null=True, verbose_name='Název módu dopravy')),
                ('slug', models.SlugField(max_length=20, unique=True, verbose_name='Identifikátor')),
                ('order', models.IntegerField(blank=True, null=True, verbose_name='Pořadí')),
                ('tooltip', models.TextField(default=None, verbose_name='Vysvětlivka módu')),
                ('tooltip_en', models.TextField(default=None, null=True, verbose_name='Vysvětlivka módu')),
                ('tooltip_cs', models.TextField(default=None, null=True, verbose_name='Vysvětlivka módu')),
                ('does_count', models.BooleanField(default=True, help_text='Počítá se jako jízda do práce/z práce.', verbose_name='Počítá se')),
            ],
        ),
        migrations.RunPython(forwards_func, reverse_func),
    ]