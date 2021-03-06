# Generated by Django 2.2.1 on 2019-05-18 18:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=250)),
                ('preparationtime', models.IntegerField(blank=True)),
                ('cooktime', models.IntegerField(blank=True)),
                ('potion_quantity', models.TextField(choices=[('Portion', 'Portionen'), ('Pieces', 'Stück')], default='Portion', max_length=100)),
                ('portion_unit', models.CharField(max_length=100)),
                ('nutrition_kcal', models.FloatField(blank=True)),
                ('nutrition_carbs', models.FloatField(blank=True)),
                ('nutrition_fat', models.FloatField(blank=True)),
                ('nutrition_protein', models.FloatField(blank=True)),
                ('note', models.TextField(blank=True)),
                ('author', models.CharField(max_length=100)),
                ('source', models.CharField(blank=True, max_length=250)),
                ('creationdate', models.DateField()),
                ('tags', models.ManyToManyField(to='recipes.Tag')),
            ],
        ),
        migrations.CreateModel(
            name='Picture',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='')),
                ('order', models.IntegerField(default=1)),
                ('description', models.CharField(blank=True, max_length=250)),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recipes.Recipe')),
            ],
        ),
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.FloatField(blank=True)),
                ('name', models.CharField(max_length=250)),
                ('group', models.CharField(blank=True, max_length=100)),
                ('order_item', models.IntegerField()),
                ('order_group', models.IntegerField(blank=True)),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recipes.Recipe')),
            ],
        ),
        migrations.CreateModel(
            name='Direction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('step', models.IntegerField()),
                ('description', models.TextField()),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recipes.Recipe')),
            ],
        ),
    ]
