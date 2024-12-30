# Generated by Django 2.2.28 on 2024-11-12 12:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dpnk', '0176_auto_20241112_1148'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='newsletter',
            field=models.CharField(blank=True, choices=[('challenge', 'Výzva'), ('events', 'Události'), ('mobility', 'Mobilita')], help_text='Odběr e-mailů můžete kdykoliv v průběhu soutěže zrušit.', max_length=30, null=True, verbose_name='Odběr zpráv prostřednictvím e-mailů'),
        ),
    ]