# Generated by Django 2.1.3 on 2019-05-03 15:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('communication', '0006_numsecteur'),
    ]

    operations = [
        migrations.AddField(
            model_name='appel',
            name='nom_appelant',
            field=models.CharField(default='non renseigne', max_length=30),
        ),
        migrations.AddField(
            model_name='appel',
            name='nom_appele',
            field=models.CharField(default='non renseigne', max_length=30),
        ),
    ]
