# Generated by Django 2.2.24 on 2022-03-14 08:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('t_shirt_delivery', '0016_deliverybatch_pickup_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='deliverybatch',
            name='wellpack_csv',
            field=models.FileField(blank=True, max_length=512, null=True, upload_to='wellpack_csv', verbose_name='Wellpack CSV tabulka'),
        ),
    ]