from recipes.models import Recipe, Tag
from recipy import settings


def search_recipes(search_string=None, tags=None):
    query = Recipe.objects.all().distinct()
    
    # TODO: optimize? //stackoverflow.com/a/8637972/4427997
    if tags:
        for tag in Tag.objects.all():
            if tags.get(tag.name, None) is None:  # value could be set to None, or not be set at all
                continue
            
            if tags[tag.name]:
                query = query.filter(tags=tag)
            else:
                query = query.exclude(tags=tag)
    
    if search_string:
        db_backend = settings.DATABASES['default']['ENGINE'].split('.')[-1]
        if db_backend == 'postgresql':
            from django.contrib.postgres.aggregates import StringAgg
            from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
            
            search_v = SearchVector('title', weight='B') \
                       + SearchVector(StringAgg('ingredient__name', delimiter=' '), weight='C') \
                       + SearchVector(StringAgg('direction__description', delimiter=' '), weight='C')
            
            terms = [SearchQuery(term + ':*', search_type='raw') for term in search_string.split()]
            search_q = terms[0]
            for sq in terms[1:]:
                search_q &= sq
            
            query = query.annotate(
                search=search_v,
                rank=SearchRank(search_v, search_q)
            ).filter(search=search_q).filter(rank__gt=0).order_by('-rank')
        
        else:
            query = query.filter(title__icontains=search_string)
    
    return query
