# Register your models here.
from django.contrib import admin
from .models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField, UserCreationForm as DjangoUserCreationForm, UserChangeForm as DjangoUserChangeForm

class CustomUserCreationForm(DjangoUserCreationForm):
    class Meta(DjangoUserCreationForm.Meta):
        model = User
        fields = ('username', 'role')

class CustomUserChangeForm(DjangoUserChangeForm):
    class Meta(DjangoUserChangeForm.Meta):
        model = User
        fields = ('username', 'role', 'password')

class UserAdmin(BaseUserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'role', 'password1', 'password2'),
        }),
    )
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Información adicional', {'fields': ('role',)}),
    )
    list_display = BaseUserAdmin.list_display + ('role',)
    list_filter = BaseUserAdmin.list_filter + ('role',)

admin.site.register(User, UserAdmin)