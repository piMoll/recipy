# Generated by Django 2.2.1 on 2019-05-20 18:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0005_auto_20190520_1532'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='resttime',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='quantity',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
