from django import forms

from django_aiproviders.models import Handle

class TestForm(forms.ModelForm):
    class Meta:
        model = Handle
        fields = ["provider", "model_name", "conversation", "context", "instruction"]
