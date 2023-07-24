from django.contrib import admin
from import_export import resources
from jalali_date.admin import TabularInlineJalaliMixin
from reports.models import *
from performanceManagement.models import Evaluation
from import_export.admin import ExportActionModelAdmin
from import_export.fields import Field
from admin_searchable_dropdown.filters import AutocompleteFilter


class EventsAgreementsResource(resources.ModelResource):
    type_report = Field(attribute='type_report', column_name='type_report')
    deadline = Field(attribute='deadline', column_name='deadline')
    date_report = Field(attribute='date_report', column_name='date_report')

    class Meta:
        model = Events_agreements
        fields = (
            'type_report', 'assessor__first_name', 'assessor__last_name', 'be_evaluated__first_name',
            'be_evaluated__last_name', 'quantitative_qualitative_goal',
            'description', 'assessment_type', 'deadline', 'date_report')
        export_order = (
            'type_report', 'assessor__first_name', 'assessor__last_name', 'be_evaluated__first_name',
            'be_evaluated__last_name', 'quantitative_qualitative_goal',
            'description', 'assessment_type', 'deadline', 'date_report')


class EventsAgreementsExport(ExportActionModelAdmin):
    resource_class = EventsAgreementsResource


class EventsAgreementsFilterBeEvaluated(AutocompleteFilter):
    title = 'ارزیابی شونده'  # display title
    field_name = 'be_evaluated'  # name of the foreign key field


class EventsAgreementsFilterAssessor(AutocompleteFilter):
    title = 'ارزیابی شونده'  # display title
    field_name = 'assessor'  # name of the foreign key field


@admin.register(Events_agreements)
class EventsAgreementsAdmin(EventsAgreementsExport, TabularInlineJalaliMixin, admin.ModelAdmin):
    list_display = (
        'type_report', 'assessor', 'be_evaluated', 'date_report', 'deadline', 'quantitative_qualitative_goal',
        'description', 'assessment_type', 'is_open_agreement', 'like_dislike')
    list_filter = (EventsAgreementsFilterBeEvaluated, EventsAgreementsFilterAssessor, 'type_report', 'assessment_type',
                   'is_open_agreement')

    search_fields = (
        'assessor__first_name', 'assessor__last_name', 'be_evaluated__first_name', 'be_evaluated__last_name',
        'description')


######################################Feedback########################################################
class FeedbackResource(resources.ModelResource):
    class Meta:
        model = Feedback_sessions
        fields = ('assessor__first_name', 'assessor__last_name', 'be_evaluated__first_name', 'be_evaluated__last_name',
                  'description', 'date_report')
        export_order = (
            'assessor__first_name', 'assessor__last_name', 'be_evaluated__first_name', 'be_evaluated__last_name',
            'description', 'date_report')


class FeedBackExport(ExportActionModelAdmin):
    resource_class = FeedbackResource


@admin.register(Feedback_sessions)
class Feedback_sessionsAdmin(FeedBackExport, admin.ModelAdmin):
    list_display = ('assessor', 'be_evaluated', 'description', 'date_report')
    list_per_page = 1000


########################################Eval_Report#################################################
class RowInlineEvaReport(admin.TabularInline):
    model = Eval_Report.evaluations.through
    max_num = 0
    fields = ['axes', 'axes_score', 'indicator', 'indicator_weight', 'item', 'item_score']
    readonly_fields = ['axes', 'axes_score', 'indicator', 'indicator_weight', 'item', 'item_score']

    def axes(self, instance):
        return Evaluation.objects.get(id=instance.evaluation_id).indicators.axes.name

    def axes_score(self, instance):
        return Evaluation.objects.get(id=instance.evaluation_id).indicators.axes.score

    def indicator(self, instance):
        return Evaluation.objects.get(id=instance.evaluation_id).indicators.name

    def indicator_weight(self, instance):
        return Evaluation.objects.get(id=instance.evaluation_id).indicators.weight

    def item(self, instance):
        return Evaluation.objects.get(id=instance.evaluation_id).items_evaluation.name

    def item_score(self, instance):
        return Evaluation.objects.get(id=instance.evaluation_id).items_evaluation.score

    axes.short_description = 'محور'
    axes_score.short_description = 'امتياز محور'
    indicator.short_description = 'شاخص'
    indicator_weight.short_description = 'وزن شاخص'
    item.short_description = 'گویه انتخاب شده'
    item_score.short_description = 'امتياز آيتم'

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Eval_Report)
class Eval_ReportAdmin(admin.ModelAdmin):
    list_display = (
        'year',
        'season',
        'assessor',
        'be_evaluated',
        'get_score',
        'display'
    )
    readonly_fields = ('year', 'season', 'assessor', 'be_evaluated',)
    inlines = [
        RowInlineEvaReport,
    ]
    search_fields = (
        'assessor__first_name', 'assessor__last_name', 'be_evaluated__first_name', 'be_evaluated__last_name')

    def get_score(self, instanse):
        return instanse.get_score()

    get_score.__name__ = 'نتیجه'
    exclude = ('evaluations',)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return True


@admin.register(QuestionForFeedbackSessions)
class QuestionForFeedbackSessionsAdmin(admin.ModelAdmin):
    list_display = ('questions',)


@admin.register(EvaluationForFeedbackSessions)
class EvaluationForFeedbackSessionsAdmin(admin.ModelAdmin):
    list_display = ('be_evaluated', 'feedback_session')
