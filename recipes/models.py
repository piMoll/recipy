import os
import random

from django.core.files.storage import FileSystemStorage
from django.db import models
import re
from django.utils import timezone

from recipy.settings import MEDIA_ROOT


class Tag(models.Model):
    BRIGHT = 'rgb(253, 246, 227)'
    DARK = 'rgb(0, 43, 54)'
    
    name = models.CharField(max_length=100, unique=True)
    color = models.CharField(max_length=50, default=DARK)
    font = models.CharField(max_length=50, default=BRIGHT, editable=False)
    
    def calc_font(self):
        """
        :see: https://stackoverflow.com/a/3943023
        :return: str
        """
        r = r"rgb\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)"
        (red, green, blue) = re.match(r, self.color).groups()

        return (
            self.DARK
            if (int(red) * 0.299 + int(green) * 0.587 + int(blue) * 0.114) > 186
            else self.BRIGHT
        )
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        self.font = self.calc_font()
        super(Tag, self).save(*args, **kwargs)


class Recipe(models.Model):
    PORTIONS = 'Portion'
    PIECES = 'Pieces'
    
    PORTION_UNIT = [
        (PORTIONS, 'Portionen'),
        (PIECES, 'Stück'),
    ]
    
    title = models.CharField(max_length=255)
    preparationtime = models.IntegerField(blank=True, null=True)
    cooktime = models.IntegerField(blank=True, null=True)
    resttime = models.IntegerField(blank=True, null=True)
    portion_quantity = models.FloatField()
    portion_unit = models.CharField(
        max_length=100,
        choices=PORTION_UNIT,
        default=PORTIONS
    )  # type: str
    nutrition_kcal = models.FloatField(blank=True, null=True)
    nutrition_carbs = models.FloatField(blank=True, null=True)
    nutrition_fat = models.FloatField(blank=True, null=True)
    nutrition_protein = models.FloatField(blank=True, null=True)
    # meant for: Tipp, Hinweis, kleine Mengen, eigene Notizen
    note = models.TextField(blank=True, default='')
    author = models.CharField(max_length=100)
    source = models.CharField(
        max_length=255,
        blank=True,
        default=''
    )
    tags = models.ManyToManyField(Tag)
    creationdate = models.DateField()
    
    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """ Set creation date """
        if not self.id:
            self.creationdate = timezone.now()
        return super(Recipe, self).save(*args, **kwargs)


class Ingredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    quantity = models.CharField(max_length=255, blank=True, default='')
    name = models.CharField(max_length=255)
    group = models.CharField(max_length=100, blank=True, default='')
    order_item = models.IntegerField()
    order_group = models.IntegerField(blank=True, null=True)
    
    def __str__(self):
        return f'{self.quantity} {self.name}'


class Direction(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    step = models.IntegerField()
    description = models.TextField()
    
    def __str__(self):
        return f'{self.step}. {self.description}'


class Picture(models.Model):
    PICTURE_ROOT = 'recipes_img'

    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=PICTURE_ROOT)
    order = models.IntegerField(default=0)
    description = models.CharField(max_length=255, blank=True, default='')
    
    def __str__(self):
        return f'Picture {self.id}'

    def save(self, *args, **kwargs):
        self.image.name = self.get_file()

        super(Picture, self).save(*args, **kwargs)

    def get_file(self):
        recipe_id = '{:04d}'.format(self.recipe_id)
        random_slug = '{:08x}'.format(random.randrange(16 ** 8))
        extension = self.image.file.content_type.split('/')[1]
        return f'{recipe_id}_{random_slug}.{extension}'
