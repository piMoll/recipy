from .wildeisen import Wildeisen

available_options = {
    'wildeisen': {
        'name': 'Annemarie Wildeisen',
        'handler': lambda jobs: Wildeisen().crawl_all(jobs)
    }
}
