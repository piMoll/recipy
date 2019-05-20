from recipes.models import Tag, Recipe, Direction, Ingredient, Picture


def createTestData():
    """
    :return:
    """

    # Test Recipe
    recipe = Recipe.objects.get(title='Test Rezept nach Grossmutters Art')
    if not recipe:
        recipe = Recipe.objects.create(
            title='Test Rezept nach Grossmutters Art',
            preparationtime=15,
            cooktime=20,
            portion_quantity=4,
            portion_unit='Portion',
            nutrition_kcal=800,
            nutrition_carbs=43,
            nutrition_fat=10.2,
            nutrition_protein=7.5,
            note='Gelingt immer!',
            author='Patricia',
            source='Eigene Rezepte'
        )
        
        recipe.tags.add(Tag.objects.get(name='hauptgericht'),
                        Tag.objects.get(name='einfach'),
                        Tag.objects.get(name='favorit'))
    
    ingredients = Ingredient.objects.filter(recipe=recipe)
    if not ingredients:
        Ingredient.objects.create(
            name='Pancetta',
            quantity='150g',
            group='Belag',
            order_item=1,
            order_group=1,
            recipe=recipe
        )
        Ingredient.objects.create(
            name='Petersilie',
            quantity='1 Bund',
            group='Belag',
            order_item=2,
            order_group=1,
            recipe=recipe
        )
        Ingredient.objects.create(
            name='Salz',
            quantity='',
            group='Belag',
            order_item=3,
            order_group=1,
            recipe=recipe
        )
        Ingredient.objects.create(
            name='Spaghetti',
            quantity='300g',
            group='Teig',
            order_item=4,
            order_group=2,
            recipe=recipe
        )
        Ingredient.objects.create(
            name='Olivenöl',
            quantity='2 EL',
            group='Teig',
            order_item=5,
            order_group=2,
            recipe=recipe
        )
        Ingredient.objects.create(
            name='Ei',
            quantity='1',
            group='Teig',
            order_item=6,
            order_group=2,
            recipe=recipe
        )
        Ingredient.objects.create(
            name='Parmesan',
            quantity='50g',
            group='Teig',
            order_item=6,
            order_group=2,
            recipe=recipe
        )
        Ingredient.objects.create(
            name='schwarzer Pfeffer',
            quantity='',
            group='Teig',
            order_item=7,
            order_group=2,
            recipe=recipe
        )
    
    directions = Direction.objects.filter(recipe=recipe)
    if not directions:
        Direction.objects.create(
            step=1,
            description="In einer Pfanne etwa 4 Liter Wasser für die Spaghetti aufkochen.",
            recipe=recipe
        )
        Direction.objects.create(
            step=2,
            description="Inzwischen den Pancetta oder Speck in ½ cm breite Streifen schneiden. Die Petersilie grob hacken.",
            recipe=recipe
        )
        Direction.objects.create(
            step=3,
            description="Das Kochwasser salzen, die Spaghetti hineingeben und bissfest garen.",
            recipe=recipe
        )
        Direction.objects.create(
            step=4,
            description="Inzwischen in einer grossen beschichteten Bratpfanne das Olivenöl erhitzen. Pancetta oder Speck darin knusprig braten.",
            recipe=recipe
        )
        Direction.objects.create(
            step=5,
            description="In einer Schüssel die Eier und den Käse gut verrühren. Die Petersilie beifügen und mit reichlich frisch gemahlenem Pfeffer würzen.",
            recipe=recipe
        )
        Direction.objects.create(
            step=6,
            description="Wenn die Spaghetti bissfest sind, mit einer Kelle gut 1 dl Kochwasser entnehmen und unter die Eier schlagen. Die Mischung wenn nötig mit Salz nachwürzen.",
            recipe=recipe
        )
        Direction.objects.create(
            step=7,
            description="Die Spaghetti abschütten, zum Pancetta oder Speck geben, gut unterziehen, dann die Ei-Käse-Creme dazugeben, alles mischen und sofort in einer vorgewärmten Schüssel anrichten. Die Carbonara sofort servieren.",
            recipe=recipe
        )
    
    pic = Picture.objects.filter(recipe=recipe)
    if not pic:
        Picture.objects.create(
            image='stubs/important_test_image.jpg',
            order=1,
            recipe=recipe,
            description='Schönes Bild'
        )


if __name__ == '__main__':
    createTestData()