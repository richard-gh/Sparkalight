from django.contrib import admin
from pet.forms import PersonCreationForm, PersonChangeForm, UserAdmin
from pet.models import Board, Picture, LikeBoard, BoardComment, Contact, Person


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


admin.site.register(Board)
admin.site.register(Picture)
admin.site.register(LikeBoard)
admin.site.register(BoardComment)
admin.site.register(Contact)
admin.site.register(Person, PersonAdmin)
