import csv
from encodings.utf_8 import encode
from django.contrib import admin
from django.http import HttpResponse
from accounts.models import Account
from performanceManagement import models
from import_export import resources
from import_export.admin import ExportActionModelAdmin
from admin_searchable_dropdown.filters import AutocompleteFilter


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


@admin.register(models.Axes)
class AxesAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = (
        'name', 'score',)
    actions = ["export_as_csv"]


########################################################
class ItemsEvaluationResource(resources.ModelResource):
    class Meta:
        model = models.Items_evaluation
        fields = ('name', 'score')
        export_order = ('name', 'score')


class ItemsEvaluationExport(ExportActionModelAdmin):
    resource_class = ItemsEvaluationResource


@admin.register(models.Items_evaluation)
class Items_evaluationAdmin(ItemsEvaluationExport, admin.ModelAdmin):
    list_display = ('name', 'score',)


####################################################################################


class RowInline(admin.TabularInline):
    model = models.Indicators.be_evaluated.through
    verbose_name_plural = 'انتخاب ارزیابی شونده ها'
    min_num = 0

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        formfield = super(RowInline, self).formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name == 'account':
            if request._place_obj is not None:
                if request._place_obj.assessor is not None:
                    formfield.queryset = formfield.queryset.filter(be_evaluated__assessor=request._place_obj.assessor)
                else:
                    formfield.queryset = formfield.queryset.filter()
            else:
                formfield.queryset = formfield.queryset.none()
        return formfield


class IndicatorsFilter(AutocompleteFilter):
    title = 'نام ارزیاب'  # display title
    field_name = 'assessor'  # name of the foreign key field


@admin.register(models.Indicators)
class IndicatorsAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = (
        'axes', 'name', 'assessor', 'weight', 'get_items')
    actions = ["export_as_csv"]
    inlines = [
        RowInline,
    ]
    exclude = ('be_evaluated',)
    list_display_links = ('name',)
    list_filter = [IndicatorsFilter,'axes']

    def get_form(self, request, obj=None, **kwargs):
        request._place_obj = obj
        return super(IndicatorsAdmin, self).get_form(request, obj, **kwargs)

    def get_items(self, instanse):
        return instanse.get_items()

    get_items.short_description = 'گویه های ارزیابی'
