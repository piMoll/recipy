from django import forms
from django.views.generic import FormView

from .adapters import available_options
import json


class ImportForm(forms.Form):
    adapter = forms.TypedChoiceField(
        choices=[(key, val['name']) for key, val in available_options.items()],
        coerce=lambda key: available_options[key]['handler']
    )
    titles = forms.CharField(widget=forms.Textarea({"cols": 80, "rows": 10}))


class ImportView(FormView):
    template_name = 'crawler/standalone.html'
    form_class = ImportForm
    success_url = '.'

    def form_valid(self, form):
        """
        This only runs after a POST
        """
        handler = form.cleaned_data['adapter']
        titles = form.cleaned_data['titles'].split('\r\n')

        # imported_recipes = {}
        # for title in titles:
        #     try:
        #         imported_recipes[title] = {
        #             'success': True,
        #             'result': handler(title).save()
        #         }
        #     except Exception as e:
        #         logging.exception(e)
        #         imported_recipes[title] = {
        #             'success': False,
        #             'result': str(e)
        #         }

        imported_recipes = handler(titles)

        success = any(
            job['success'] for job in imported_recipes.values()
        )

        import_result = {
            'success': success,
            'data': imported_recipes,
        }
        import_result = json.dumps(import_result, indent=4, ensure_ascii=False)

        self.extra_context = {"processed_imports": import_result}

        return self.render_to_response(self.get_context_data())
