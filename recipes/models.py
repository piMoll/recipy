import random
from django.db import models
import re
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify


def get_slug(length):
    return '{slug:0{length}x}'.format(length=length,
                                      slug=random.randrange(16 ** length))

def format_duration(duration):
    if not duration:
        return ''
    duration_str = ''
    hours = duration // 60
    if hours:
        duration_str = duration_str + f"{hours} h "
    duration = duration % 60
    if duration:
        minutes = duration
        duration_str = duration_str + f"{minutes} min"
    return duration_str

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

    def query_key(self):
        return f'tag.{self.name}'
    
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
    author = models.CharField(max_length=100, blank=True)
    source = models.CharField(
        max_length=255,
        blank=True,
        default=''
    )
    tags = models.ManyToManyField(Tag, blank=True)
    creationdate = models.DateField()
    public_slug = models.CharField(max_length=10, unique=True, null=False)
    
    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """ Set creation date and slug """
        if not self.id:
            self.creationdate = timezone.now()
            # Public link
            self.public_slug = get_slug(10)
            while Recipe.objects.filter(public_slug=self.public_slug).exists():
                self.public_slug = get_slug(10)

        return super(Recipe, self).save(*args, **kwargs)

    def get_display_slug(self):
        return slugify(self.title)

    def get_absolute_url(self):
        return reverse('recipes:detail', kwargs={'pk': self.pk, 'slug': self.get_display_slug()})
    
    def get_public_url(self):
        return reverse('recipes:public', kwargs={'public_slug': self.public_slug})
    
    def tags_sorted(self):
        return self.tags.order_by('pk')


class Ingredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    quantity = models.CharField(max_length=255, blank=True, default='')
    name = models.CharField(max_length=255)
    group = models.CharField(max_length=100, blank=True, default='')
    order_item = models.IntegerField()
    
    class Meta:
        ordering = ['order_item']
    
    def __str__(self):
        return f'{self.quantity} {self.name}'


class Direction(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    step = models.IntegerField()
    description = models.TextField()
    
    class Meta:
        ordering = ['step']
    
    def __str__(self):
        return f'{self.step}. {self.description}'


class Picture(models.Model):
    PICTURE_ROOT = 'recipes_img'
    THUMBNAIL_ROOT = 'recipes_tmb'

    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=PICTURE_ROOT, null=False, blank=False)
    thumbnail = models.ImageField(upload_to=THUMBNAIL_ROOT, null=False, blank=True)
    order = models.IntegerField(default=0)
    description = models.CharField(max_length=255, blank=True, default='')
    
    def __str__(self):
        return f'Picture {self.id}'

    def save(self, *args, **kwargs):
        if not self.id:
            self.thumbnail = self.make_thumbnail(self.image.file)
            name = self._get_filename()
            self.image.name = name
            self.thumbnail.name = name
        else:
            # Todo: check if the image has change and raise if so
            pass

        super().save(*args, **kwargs)

    def delete(self, using=None, keep_parents=False):
        self.image.delete(save=False)
        self.thumbnail.delete(save=False)
        super().delete(using=using, keep_parents=keep_parents)

    def _get_filename(self):
        if self.id:
            raise RuntimeError('Not safe to call _get_filename after object has been saved')

        recipe_id = f'{self.recipe_id:04d}'
        random_slug = get_slug(8)
        extension = self.image.file.content_type.split('/')[1]
        return f'{recipe_id}_{random_slug}.{extension}'

    THUMBNAIL_HEIGHT_RATIO = 0.55
    THUMBNAIL_WIDTH = 540

    def make_thumbnail(self, file):
        from PIL import Image
        from io import BytesIO
        from django.core.files.base import ContentFile

        image = Image.open(file)
        image.load()
        file_type = image.format
        image = image.copy()

        w, h = self.THUMBNAIL_WIDTH, self.THUMBNAIL_HEIGHT_RATIO * self.THUMBNAIL_WIDTH

        image = self.crop_to_ratio(image, w / h)
        image.thumbnail((w, h))

        buffer = BytesIO()
        image.save(buffer, format=file_type)
        return ContentFile(buffer.getbuffer())

    @staticmethod
    def crop_to_ratio(image, ratio):
        W, H = 1, 1 / ratio
        w, h = image.size

        r = min(w, h/H)
        w1, h1 = r * W, r * H
        x0, y0 = (w - w1) / 2, (h - h1) / 2
        x1, y1 = x0 + w1, y0 + h1

        box = (x0, y0, x1, y1)
        box = [round(dim) for dim in box]

        return image.crop(box)

    def b64image(self):
        import base64
        file = self.image.file
        with file.open('rb') as fh:
            code = base64.b64encode(fh.read())
        return code.decode('utf-8')


class Collection(models.Model):
    name = models.CharField(max_length=255, unique=True)
    recipes = models.ManyToManyField(Recipe)
    public_slug = models.CharField(max_length=10, unique=True, null=False)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        """ Set slug """
        if not self.id:
            # Public link
            self.public_slug = get_slug(10)
            while Collection.objects.filter(public_slug=self.public_slug).exists():
                self.public_slug = get_slug(10)

        return super(Collection, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('recipes:collection_detail', kwargs={'pk': self.pk})
