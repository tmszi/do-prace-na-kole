# Generated by Django 2.2.10 on 2020-03-03 14:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('t_shirt_delivery', '0014_deliverybatch_combined_opt_pdf'),
    ]

    operations = [
        migrations.AddField(
            model_name='tshirtsize',
            name='code',
            field=models.CharField(default='', max_length=80, null=True, verbose_name='Kód v skladu'),
        ),
    ]