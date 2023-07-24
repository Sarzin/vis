import csv
from typing import Set
from encodings.utf_8 import encode
from performanceManagement.admin import IndicatorsAdmin
from django_jalali.admin.filters import JDateFieldListFilter
from jalali_date import datetime2jalali, date2jalali
from jalali_date.admin import ModelAdminJalaliMixin, StackedInlineJalaliMixin, TabularInlineJalaliMixin
from django.contrib import admin
from jalali_date import datetime2jalali
from .forms import *
from accounts.models import Account, Unit, staff_assessor
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.http import HttpResponse


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

class ExportCsvMixin:
    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response, encode('utf8'))

        writer.writerow(field_names)
        for obj in queryset:
            row = writer.writerow([getattr(obj, field) for field in field_names])

        return response

    export_as_csv.short_description = "دانلود اطلاعات"


@admin.register(Account)
class AccountAdmin(TabularInlineJalaliMixin, admin.ModelAdmin, ExportCsvMixin):
    list_display = (
        'first_name', 'last_name', 'username', 'unit', 'phone_number', 'is_active', 'assessor', 'join_date',)
    actions = ["export_as_csv"]
    add_form = UserCreationForm
    change_form = UserAdminChangeForm
    # filter_horizontal = ('groups', 'user_permissions',)
    # readonly_fields = ('password',)
    list_display_links = ['username', 'first_name', 'last_name']
    list_filter = (
        ('join_date', JDateFieldListFilter), 'assessor'
    )
    list_per_page = 1000
    search_fields = ('first_name', 'last_name')
    autocomplete_fields =['unit']

    def get_form(self, request, obj=None, **kwargs):
        if not obj:
            self.form = self.add_form
        else:
            self.form = self.change_form
        form = super().get_form(request, obj, **kwargs)
        is_superuser = request.user.is_superuser
        disabled_fields = set()  # type: Set[str]

        if not is_superuser:
            disabled_fields |= {
                'is_superuser',
                'user_permissions',
                'groups'
            }
        for f in disabled_fields:
            if f in form.base_fields:
                form.base_fields[f].disabled = True
        form.base_fields['last_login'].disabled = True
        return form
        # return super(AccountAdmin, self).get_form(request, obj, **kwargs)

    # The fields to be used in displaying the User model.


@admin.register(staff_assessor)
class staff_assessor(admin.ModelAdmin, ExportCsvMixin):
    list_display = (
        "assessor", 'staff',)
    actions = ["export_as_csv"]
    list_per_page = 1000
    autocomplete_fields = ['assessor', 'staff']


class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    change_form = UserChangeForm
    add_form = UserCreationForm
    list_display = ('email', 'first_name', 'last_name', 'username', 'phone_number', 'admin', 'is_active',)

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    # list_display = ('email', 'date_of_birth', 'is_admin')
    list_filter = ('is_active',)
    fieldsets = (
        (None, {'fields': ('email', 'password', 'username', 'first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'groups', 'permissions')}),

    )
    # # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password', 'username', 'first_name', 'last_name')}
         ),
    )
    search_fields = ('email',)
    ordering = ('email',)

# admin.site.unregister(Group)
# admin.site.register(UserAdmin)
