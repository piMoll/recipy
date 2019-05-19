from django.db import models
import re


class Tag(models.Model):
    BRIGHT = 'rgb(253, 246, 227)'
    DARK = 'rgb(0, 43, 54)'
    
    name = models.CharField(max_length=100, unique=True)
    color = models.CharField(max_length=50, default=DARK)
    
    @property
    def font(self):
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
    potion_quantity = models.FloatField()
    portion_unit = models.CharField(
        max_length=100,
        choices=PORTION_UNIT,
        default=PORTIONS
    )
    nutrition_kcal = models.FloatField(blank=True, null=True)
    nutrition_carbs = models.FloatField(blank=True, null=True)
    nutrition_fat = models.FloatField(blank=True, null=True)
    nutrition_protein = models.FloatField(blank=True, null=True)
    note = models.TextField(blank=True, default='')
    author = models.CharField(max_length=100)  # new: Name of User or Crawler
    source = models.CharField(
        max_length=255,
        blank=True,
        default=''
    )  # new: wildeisen.ch, bettybossy.ch, own... or url?
    creationdate = models.DateField()  # new
    tags = models.ManyToManyField(Tag)
    
    def __str__(self):
        return self.title


class Ingredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    quantity = models.FloatField(blank=True, null=True)
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
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    image = models.ImageField()
    order = models.IntegerField(default=0)
    description = models.CharField(max_length=255, blank=True, default='')
    
    def __str__(self):
        return f'Picture {self.id}'