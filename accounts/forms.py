from django.contrib.auth.forms import ReadOnlyPasswordHashField, UserChangeForm

from .models import *
from django import forms


class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""

    # password1 = forms.CharField(label='رمز عبور', widget=forms.PasswordInput)
    # password2 = forms.CharField(label='تایید رمز عبور', widget=forms.PasswordInput)

    class Meta:
        model = Account
        fields = "__all__"
        # exclude = ['password',]

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password")
        return password1

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth import get_user_model


class UserAdminChangeForm(forms.ModelForm):
    """
    A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField(
        label="گذر واژه",
        help_text=_(
            "Passwords are not saved as plan texts then there is no way to see this user's password."
            " You can just change them. in order to change password, <a href='/auth/change_user_pass'>click here</a>."
        )
    )

    class Meta:
        model = get_user_model()
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(UserAdminChangeForm, self).__init__(*args, **kwargs)

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value.
        return self.initial["password"]

    def save(self, commit=True):
        user = super(UserAdminChangeForm, self).save(commit=False)
        return user


class chaneg_pass_Form(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['username', 'password']
        widgets = {
            'status': forms.Select(
                attrs={
                    'class': 'form-control',
                }
            ),

        }
