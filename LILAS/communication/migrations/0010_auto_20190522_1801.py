# Generated by Django 2.1.3 on 2019-05-22 16:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('communication', '0009_lif'),
    ]

    operations = [
        migrations.AddField(
            model_name='appel',
            name='SDA',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='appel',
            name='SUTP',
            field=models.BooleanField(default=False),
        ),
    ]
