from recipes.models import Tag

tags = [
    ['dessert', 'rgb(211, 54, 130)'],       # magenta
    ['gemüse', 'rgb(133, 153, 0)'],         # olive
    ['fleisch', 'rgb(220, 50, 47)'],        # red
    ['fisch', 'rgb(38, 139, 210)'],         # blue
    ['beilage', 'rgb(181, 137, 0)'],        # yellow
    ['drink', 'rgb(178, 111, 247)'],        # pink
    ['sauce', 'rgb(108, 113, 196)'],        # violet
    ['tapas', 'rgb(203, 75, 22)'],          # orange
    ['hauptgericht', 'rgb(7, 54, 66)'],     # dark blue
    ['einfach', 'rgb(208, 229, 69)'],       # light green
    ['leicht', 'rgb(42, 161, 152)'],        # cyan
    ['favorit', 'rgb(232, 222, 23)'],       # light yellow
    ['todo', 'rgb(253, 246, 227)'],         # beige
    ['unvollständig', 'rgb(101, 123, 131)'], # grey
]


def initData():
    """
    run in django console:
    import initData
    initData.initData()
    
    :return:
    """
    for tag in tags:
        [name, color] = tag
        t = Tag.objects.create(name=name, color=color)
        t.save()
        


if __name__ == '__main__':
    initData()