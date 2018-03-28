from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ObjectDoesNotExist
from .models import *
import re
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.core.exceptions import ValidationError


class UserRegistration(forms.Form):
    username = forms.CharField(error_messages={'required': 'The username field is required'})
    email = forms.EmailField(error_messages={'required': 'The email field is required'})
    date_of_birth = forms.DateField(widget=forms.SelectDateWidget(years=range(1950, 2012)))
    password = forms.CharField(
        widget=forms.PasswordInput(render_value=False)
    )

    MIN_LENGTH = 6

    def clean_password(self):
        password = self.cleaned_data['password']

        if len(password) < self.MIN_LENGTH:
            raise forms.ValidationError("The new password must be at least %d characters long." % self.MIN_LENGTH)

        return password

    def clean_username(self):
        username = self.cleaned_data['username']
        if Person.objects.filter(username=username).exists():
            raise forms.ValidationError("That user is already taken")
        if not re.match(r'^[A-Za-z0-9_-]+$', username):
            raise forms.ValidationError("Sorry , you can only have alphanumeric, _ or - in username")
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if Person.objects.filter(email=email).exists():
            raise forms.ValidationError("That email is already taken")

        return email


class LoginForm(forms.Form):
    email = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput(render_value=False))

    def clean(self):

        user = self.authenticate_via_email()
        if not user:

            raise forms.ValidationError("Sorry, that login was invalid. Please try again.")
        else:

            self.user = user
        return self.cleaned_data

    def authenticate_user(self):
        return authenticate(username=self.user.username, password=self.cleaned_data['password'])

    def authenticate_via_email(self):

        email = self.cleaned_data.get('email', None)
        if email:
            try:
                user = Person.objects.get(email__iexact=email)
                if user.is_active == False:
                    return None
                if user.check_password(self.cleaned_data['password']):
                    return user
            except ObjectDoesNotExist:
                pass
        return None


class PersonForm(forms.ModelForm):
    description = forms.CharField(max_length=230, required=False, widget=forms.Textarea)

    def clean_image(self):
        cleaned_data = super(PersonForm, self).clean()
        image = cleaned_data.get("image")

        if image:
            if image._size > 4 * 1024 * 1024:
                raise forms.ValidationError("Image Must be <4mb Less")
            if not image.name[-3:].lower() in ['jpg', 'png', ]:
                raise forms.ValidationError("Your file extension was not recongized")
            return image

    class Meta:
        model = Person
        fields = ('name', 'image',)


class ProfileForm(forms.ModelForm):
    image = forms.ImageField(required=False)
    description = forms.CharField(max_length=250, required=False, widget=forms.Textarea)
    checkbox = forms.BooleanField(required=False)

    def clean_image(self):
        cleaned_data = super(ProfileForm, self).clean()
        image = cleaned_data.get("image")

        if image:
            if image._size > 4 * 1024 * 1024:
                raise forms.ValidationError("Image Must be <4mb Less")
            if not image.name[-3:].lower() in ['jpg', 'png', ]:
                raise forms.ValidationError("Your file extension was not recongized")
            return image

    class Meta:
        model = Person
        fields = ('name', 'inbox', 'profile', 'description',)


class BoardForm(forms.ModelForm):
    text = forms.CharField(required=False, widget=forms.Textarea, max_length=200, )
    description = forms.CharField(required=False, widget=forms.Textarea, max_length=500, )

    image = forms.ImageField(required=False)

    def clean_image(self):
        cleaned_data = super(BoardForm, self).clean()
        image = cleaned_data.get("image")

        if image:
            if image._size > 4 * 1024 * 1024:
                raise forms.ValidationError("Image Must be <4mb Less")
            if not image.name[-3:].lower() in ['jpg', 'png', ]:
                raise forms.ValidationError("Your file extension was not recongized")
            return image

    class Meta:
        model = Board
        fields = ('name', 'shirt_size',)


class PictureForm(forms.ModelForm):
    description = forms.CharField(widget=forms.Textarea, max_length=120, required=False)
    image = forms.ImageField(required=True)

    def __init__(self, user, *args, **kwargs):
        super(PictureForm, self).__init__(*args, **kwargs)
        self.fields['board'].queryset = Board.objects.filter(user=user)

    class Meta:
        model = Picture
        fields = ('image', 'board',)


class BoardDeleteForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        super(BoardDeleteForm, self).__init__(*args, **kwargs)
        self.fields['board'].queryset = Board.objects.filter(user=user)

    class Meta:
        model = Picture
        fields = ('board',)


class SearchForm(forms.Form):
    text = forms.CharField()


#class SearchBoardForm(forms.ModelForm):
#    text = forms.CharField()
#
#    class Meta:
#        model = Board
#        fields = ('shirt_size',)


class CommentsForm(forms.Form):
    text = forms.CharField(label="")


class BoardNameForm(forms.ModelForm):
    boardname = forms.CharField(max_length=55)

    def __init__(self, user, *args, **kwargs):
        super(BoardNameForm, self).__init__(*args, **kwargs)
        self.fields['board'].queryset = Board.objects.filter(user=user)

    class Meta:
        model = Picture
        fields = ('board', 'boardname',)


class BoardPictureForm(forms.ModelForm):

    def __init__(self, user, *args, **kwargs):
        super(BoardPictureForm, self).__init__(*args, **kwargs)
        self.fields['board'].queryset = Board.objects.filter(user=user)

    class Meta:
        model = Picture
        fields = ('board',)


class PictureDeleteForm(forms.ModelForm):

    def __init__(self, user, *args, **kwargs):
        super(PictureDeleteForm, self).__init__(*args, **kwargs)
        self.fields['board'].queryset = Board.objects.filter(user=user)

    class Meta:
        model = Picture
        fields = ('board',)


class BoardCommentForm(forms.ModelForm):
    body = forms.CharField(widget=forms.Textarea, max_length=100)
    hidden_field = forms.CharField(widget=forms.HiddenInput())

    class Meta:
        model = BoardComment
        fields = ()


class BoardTransferForm(forms.ModelForm):

    def __init__(self, user, *args, **kwargs):
        super(BoardTransferForm, self).__init__(*args, **kwargs)
        self.fields['board'].queryset = Board.objects.filter(user=user)

    class Meta:
        model = Picture
        fields = ('board',)


class BoardChangeNameForm(forms.ModelForm):

    def __init__(self, user, *args, **kwargs):
        super(BoardChangeNameForm, self).__init__(*args, **kwargs)
        self.fields['board'].queryset = Board.objects.filter(user=user)

    class Meta:
        model = Picture
        fields = ('board',)


class BoardDescriptionForm(forms.ModelForm):
    description = forms.CharField(widget=forms.Textarea, max_length=300)
    id = forms.CharField(widget=forms.HiddenInput())

    class Meta:
        model = Board
        fields = ('id', 'description')


class BoardPrivateForm(forms.ModelForm):

    def __init__(self, user, *args, **kwargs):
        super(BoardPrivateForm, self).__init__(*args, **kwargs)
        self.fields['board'].queryset = Board.objects.filter(user=user)

    class Meta:
        model = Picture
        fields = ('board',)


class SpecialBoardForm(forms.ModelForm):
    class Meta:
        model = Board
        fields = ('profile', 'comments', 'friends',)


class ContactForm(forms.ModelForm):
    text = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = Contact
        fields = ('email', 'Category',)


class DescriptionForm(forms.ModelForm):
    boolean = forms.BooleanField(required=False)
    description = forms.CharField(widget=forms.Textarea, required=False, max_length=22000)
    primary = forms.BooleanField(required=False)

    class Meta:
        model = Picture
        fields = ('description', 'boolean', 'primary',)


class EmailForm(forms.Form):
    old = forms.EmailField(required=False)
    email = forms.EmailField(required=False)

    def old_email(self):
        old = self.cleaned_data['old']
        person = Person.objects.get(username=request.user)
        persons = Person.objects.get(email=old)

        if persons.email == person.email:
            raise forms.ValidationError("Incorrect email")
        return old

    def clean_email(self):
        email = self.cleaned_data['email']
        if Person.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is not available")
        return email

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super(EmailForm, self).__init__(*args, **kwargs)


class SearchBoardForm(forms.ModelForm):
    class Meta:
        model = Board
        fields = ('shirt_size',)

    def __init__(self, *args, **kwargs):
        super(SearchBoardForm, self).__init__(*args, **kwargs)
        self.fields["shirt_size"].choices = [("all", "Everything"), ] + list(self.fields["shirt_size"].choices)[1:]
        self.fields["search_key"] = forms.CharField()


class BoardCommentForm(forms.ModelForm):
    body = forms.CharField(widget=forms.Textarea, max_length=100)
    hidden_field = forms.CharField(widget=forms.HiddenInput())

    class Meta:
        model = BoardComment
        fields = ()


class PersonCreationForm(forms.ModelForm):
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput)

    class Meta:
        model = Person
        fields = ('email', 'username')

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(PersonCreationForm,
                     self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class PersonChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = Person
        fields = "__all__"

    def clean_password(self):
        # Regardless of what the user provides, return the
        # initial value. This is done here, rather than on
        # the field, because the field does not have access
        # to the initial value
        return self.initial["password"]


class PersonAdmin(UserAdmin):
    add_form = PersonCreationForm
    form = PersonChangeForm

    list_display = ('email', 'is_staff', 'username', 'date_of_birth', 'inbox', 'image',)
    list_filter = ('is_staff', 'is_superuser',
                   'is_active', 'groups')
    search_fields = ('email', 'username')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)
    fieldsets = (
        (None, {'fields': ('email', 'password', 'date_of_birth', 'inbox', 'image', 'name')}),
        ('Personal info', {'fields':
                               ('username',)}),
        ('Permissions', {'fields': ('is_active',
                                    'is_staff',
                                    'is_superuser',
                                    'groups',
                                    'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),

    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username',
                       'password1', 'date_of_birth',)}
         ),
    )
