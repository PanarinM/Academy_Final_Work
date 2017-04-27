from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from django.contrib.auth.models import Group

from users.forms import UserChangeForm, UserCreationForm
from users.models import User


class CustomUserAdmin(UserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ('username', 'lastname', 'email', 'phone')
    list_filter = ('username',)
    search_fields = ('username',)
    ordering = ('username',)

    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal info', {'fields': ('firstname', 'lastname', 'country', 'birthday', 'avatar', 'phone')}),
        ('Address', {'fields': ('city', 'street', 'house',)}),
        ('Permissions', {'fields': ('is_admin',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'phone', 'password1', 'password2')}
         ),
    )
    filter_horizontal = ()

admin.site.register(User, CustomUserAdmin)
admin.site.unregister(Group)
