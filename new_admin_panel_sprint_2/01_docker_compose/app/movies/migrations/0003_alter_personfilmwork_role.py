# Generated by Django 3.2 on 2022-04-18 09:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0002_auto_20220406_0817'),
    ]

    operations = [
        migrations.AlterField(
            model_name='personfilmwork',
            name='role',
            field=models.TextField(choices=[('actor', 'Actor'), ('director', 'Director'), ('writer', 'Writer')], null=True, verbose_name='role'),
        ),
    ]
