# Generated by Django 2.0.4 on 2018-04-28 09:57

import django.contrib.gis.db.models.fields
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dpnk', '0097_auto_20180415_1240'),
    ]

    operations = [
        migrations.AddField(
            model_name='commutemode',
            name='eco',
            field=models.BooleanField(default=True, verbose_name='Ekologický'),
        ),
        migrations.AlterField(
            model_name='trip',
            name='distance',
            field=models.FloatField(blank=True, default=None, null=True, validators=[django.core.validators.MaxValueValidator(1000), django.core.validators.MinValueValidator(0)], verbose_name='Ujetá vzdálenost (Km)'),
        ),
        migrations.AlterField(
            model_name='trip',
            name='track',
            field=django.contrib.gis.db.models.fields.MultiLineStringField(blank=True, geography=True, help_text='\n<ul>\n   <li><strong>Zadávání trasy zahájíte kliknutím na tlačítko <span style="display: inline-block;" class="leaflet-draw-toolbar leaflet-bar leaflet-draw-toolbar-top"><a class="leaflet-draw-draw-polyline" href="#"></a></span>.</strong></li>\n   <li>Další body zadáváte kliknutím do mapy, <strong>cílový bod zadáte dvouklikem.</strong></li>\n   <li>Změnu trasy provedete po přepnutí do režimu úprav (<span style="display: inline-block;" class="leaflet-draw-toolbar leaflet-bar"><a class="leaflet-draw-edit-edit" href="#"></a></span>) kliknutím na trasu.</li>\n   <li>Trasu stačí zadat tak, že bude zřejmé, kterými ulicemi vede.\n   (Zadání přesnějšího průběhu nám však může pomoci lépe zjistit, jak se lidé na kole pohybují.)</li>\n   <li>Trasu bude možné změnit nebo upřesnit i později v průběhu soutěže.\n   (Trasy za jednotlivé dny však jen 7 dní nazpět.)</li>\n   <li>Polohu začátku a konce trasy stačí zadávat se 100m přesností.</li>\n</ul>\nTrasa slouží k výpočtu vzdálenosti a pomůže nám lépe určit potřeby lidí pohybuících se ve městě na kole.\n<br/>Trasy všech účastníků budou v anonymizované podobě zobrazené na <a href="https://mapa.prahounakole.cz/?zoom=13&lat=50.08741&lon=14.4211&layers=_Wgt">mapě Prahou na kole</a>.\n', null=True, srid=4326, verbose_name='trasa'),
        ),
        migrations.AlterField(
            model_name='userattendance',
            name='distance',
            field=models.FloatField(blank=True, default=None, help_text='Průměrná ujetá vzdálenost z domova do práce (v km v jednom směru)', null=True, verbose_name='Vzdálenost (km)'),
        ),
    ]
