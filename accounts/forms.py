from django import forms


class TerminationForm(forms.Form):
    final = forms.CharField(widget=forms.Textarea, max_length=500, required=False)
