from recipes.models import Tag

tags = [
    ['favorit', 'rgb(236, 209, 12)'], # yellow
    ['hauptgericht', 'rgb(38, 139, 210)'], # blue
    ['dessert', 'rgb(211, 54, 130)'], # magenta
    ['gemüse', 'rgb(133, 153, 0)'], # olive
    ['fleisch', 'rgb(220, 50, 47)'], # red
    ['fisch', 'rgb(38, 180, 210)'], # bright blue
    ['beilage', 'rgb(181, 137, 0)'], # dark yellow
    ['sauce', 'rgb(101, 123, 131)'], # grey
    ['drink', 'rgb(203, 75, 22)'],  # orange
    ['tapas', 'rgb(108, 113, 196)'], # violet
    ['einfach', 'rgb(42, 161, 152)'], # cyan
    ['leicht', 'rgb(238, 232, 213)'], # light grey
    ['todo', 'rgb(235, 240, 152)'],  # bright green
    ['unvollständig', 'rgb(7, 54, 66)'], # dark blue
]


def initData():
    """
    run in django console:
    import initData
    initData.initData()
    
    :return:
    """

    # delete all existing tags
    Tag.objects.all().delete()

    # insert tags
    for tag in tags:
        [name, color] = tag
        t = Tag.objects.create(name=name, color=color)
        t.save()
        


if __name__ == '__main__':
    initData()