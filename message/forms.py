from django import forms
from django.contrib.auth.models import User

from message.models import Person, Thread, Message


class ReplyForm(forms.Form):
    body = forms.CharField(widget=forms.Textarea, required=False, max_length=1)
    hidden_field = forms.CharField(widget=forms.HiddenInput())


class NewMessageForm(forms.ModelForm):
    recipient = forms.CharField(required=False, max_length=15)
    message = forms.CharField(widget=forms.Textarea, required=True, max_length=15)

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super(NewMessageForm, self).__init__(*args, **kwargs)

    def clean_recipient(self):

        recipient = self.cleaned_data['recipient']
        person = Person.objects.get(username=self.request.user)
        if person.inbox == "D":
            raise forms.ValidationError("You have deactivated your inbox , Please enable it at profile settings")
        if recipient:
            try:
                recipient = Person.objects.get(username=recipient)
            except Person.DoesNotExist:
                raise forms.ValidationError("This username does not exist or leave blank for saving as draft")
            return recipient
        else:

            return recipient

    class Meta:
        model = Thread
        fields = ('subject',)


class DraftForm(forms.ModelForm):
    recipient = forms.CharField(required=True, max_length=51)
    body = forms.CharField(widget=forms.Textarea, required=True, max_length=51)
    hidden_field = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super(DraftForm, self).__init__(*args, **kwargs)

    def clean_recipiet(self):

        recipient = self.cleaned_data['recipient']
        person = Person.objects.get(username=self.request.user)
        if person.inbox == "D":
            raise forms.ValidationError("You have deactivated your inbox , Please enable it at profile settings")
        if recipient:

            try:
                recipient = Person.objects.get(username=recipient)
            except User.DoesNotExist:
                raise forms.ValidationError("This username does not exist")
            return recipient

    class Meta:
        model = Message
        fields = ('body',)

    def clean_recipient(self):
        recipient = self.cleaned_data['recipient']

        try:
            recipient = User.objects.get(username=recipient)
        except User.DoesNotExist:
            raise forms.ValidationError("This username does not exist")
        return recipient


class ThreadForm(forms.ModelForm):
    class Meta:
        model = Thread
        fields = ('subject',)


class CheckBoxForm(forms.ModelForm):
    checkbox = forms.BooleanField(required=False)
    hidden_field = forms.CharField(widget=forms.HiddenInput())

    class Meta:
        model = Message
        fields = ('hidden_field',)
