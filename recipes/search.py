from recipes.models import Recipe, Tag
from django.db.models import Q, Count
from django.contrib.postgres.aggregates import StringAgg
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank


def search_recipes(search_string=None, tags=None):
    query = Recipe.objects.all().distinct()
    
    # TODO: optimize? //stackoverflow.com/a/8637972/4427997
    if tags:
        for tag in Tag.objects.all():
            # Value could be set to None, or not be set at all
            if tags.get(tag.name, None) is None: 
                continue
            
            if tags[tag.name]:
                query = query.filter(tags=tag)
            else:
                query = query.exclude(tags=tag)
    
    if search_string:
        # First, search for word parts in title. Full text search bellow can't
        #  do word parts.
        contains_parts = Q()
        for word in search_string.split(' '):
            contains_parts = contains_parts | Q(title__icontains=word)
        
        contains_in_title_query = query.filter(contains_parts).annotate(rank=Count('id')).distinct()

        # Now let's do full text search. This will ignore filler words 
        #  and rank results by number of occurrences
        # Weights are: A = 1.0, B = 0.4, C = 0.2, D = 0.1
        search_v = SearchVector('title', weight='B', config='german') \
                   + SearchVector(StringAgg('ingredient__name', delimiter=' '), 
                                  weight='C', config='german') \
                   + SearchVector(StringAgg('direction__description', delimiter=' '), 
                                  weight='C', config='german')
        # Limitation: Full text search can find terms if they are at the
        #  beginning of the word (term + wildcard), but not at the end. 
        terms = [SearchQuery(term + ':*', search_type='raw', config='german') for term in search_string.split()]
        search_q = terms[0]
        for sq in terms[1:]:
            search_q |= sq
        
        # Create a query with ranked results, filter out any results with no finds
        text_search_query = query.annotate(
            search=search_v,
            rank=SearchRank(search_v, search_q)
        ).filter(search=search_q).filter(rank__gt=0).order_by('-rank')
        
        # Combine title searches (including postfix searches) and ranked 
        # full text searches. The combined query will return distinct results.
        query = (contains_in_title_query | text_search_query).order_by('-rank')

    return query
