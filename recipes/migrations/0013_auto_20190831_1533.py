# Generated by Django 2.2.1 on 2019-08-31 13:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0012_collection_public_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collection',
            name='public_slug',
            field=models.CharField(max_length=10, unique=True),
        ),
    ]
