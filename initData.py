tags = [    ['favorit', 'rgb(236, 209, 12)'], # yellow    ['hauptgericht', 'rgb(38, 139, 210)'], # blue    ['dessert', 'rgb(211, 54, 130)'], # magenta    ['gemüse', 'rgb(86, 128, 18)'], # olive    ['fleisch', 'rgb(145, 27, 48)'], # brodeaux    ['fisch', 'rgb(78, 173, 193)'], # bright blue    ['beilage', 'rgb(181, 137, 0)'], # dark yellow    ['sauce', 'rgb(101, 123, 131)'], # grey    ['drink', 'rgb(236, 103, 103)'],  # pink    ['tapas', 'rgb(108, 113, 196)'], # violet    ['schnell', 'rgb(19, 185, 143)'], # teal    ['leicht', 'rgb(238, 232, 213)'], # light grey    ['todo', 'rgb(235, 240, 152)'],  # bright green    ['unvollständig', 'rgb(8, 95, 117)'], # dark blue    ['ungetestet', 'rgb(128, 96, 77)'],  # brown]def initData():    """    run in django console:    import initData    initData.initData()        :return:    """    from recipes.models import Tag    # delete all existing tags    # Tag.objects.all().delete()    # insert tags    for tag in tags:        [name, color] = tag        t = Tag.objects.get(name=name)        if t:            t.color = color        else:            t = Tag.objects.create(name=name, color=color)        t.save()        if __name__ == '__main__':    initData()