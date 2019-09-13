from django import forms
from django.views.generic import FormView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from .adapters import available_options
import json


class ImportForm(forms.Form):
    adapter = forms.TypedChoiceField(
        choices=[(key, val['name']) for key, val in available_options.items()],
        coerce=lambda key: available_options[key]['handler']
    )
    titles = forms.CharField(widget=forms.Textarea({"cols": 80, "rows": 10}))


class ImportView(LoginRequiredMixin, PermissionRequiredMixin, FormView):
    template_name = 'crawler/index.html'
    form_class = ImportForm
    permission_required = ('recipes.add_recipe',)
    raise_exception = True

    def form_valid(self, form):
        """
        This only runs after a POST
        """
        handler = form.cleaned_data['adapter']
        titles = form.cleaned_data['titles'].split('\r\n')

        processed_imports = handler(titles)

        success = any(
            job['success'] for job in processed_imports.values()
        )

        import_result = {
            'success': success,
            'data': processed_imports,
        }
        import_result = json.dumps(import_result, indent=4, ensure_ascii=False)

        self.extra_context = {
            'import_result': import_result,
            'processed_imports': processed_imports.values()
        }

        return self.render_to_response(self.get_context_data())
