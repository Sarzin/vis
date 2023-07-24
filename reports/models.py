from django.db import models
from accounts.models import Account
from performanceManagement.models import Indicators, Evaluation
from django_jalali.db import models as jmodels


class Events_agreements(models.Model):
    class Meta:
        verbose_name = "گزارش وقایع و توافق ها"
        verbose_name_plural = " گزارش وقایع و توافق ها"

    type = (
        ('E', 'واقعه'),
        ('A', 'توافق'),
    )
    ACCEPTABLE_FORMATS = ['%d-%m-%Y',  # '25-10-2006'
                          '%d/%m/%Y',  # '25/10/2006'
                          '%d/%m/%y']  # '25/10/06'
    limit_assessor = models.Q(assessor=True)
    type_report = models.CharField(max_length=1, choices=type, verbose_name="جنس")
    assessor = models.ForeignKey(Account, limit_choices_to=limit_assessor, on_delete=models.CASCADE,
                                 related_name="assessor_events_agreements",
                                 verbose_name="ارزیابی کننده")
    be_evaluated = models.ForeignKey(Account, on_delete=models.CASCADE,
                                     related_name="to_be_evaluated_events_agreements", verbose_name="ارزیابی شونده")
    date_report = jmodels.jDateField(auto_now_add=False, verbose_name="تاریخ ثبت", null=True, blank=True)
    deadline = jmodels.jDateField(auto_now_add=False, verbose_name='موعد انجام', null=True, blank=True)
    quantitative_qualitative_goal = models.TextField(null=True, blank=True, verbose_name="هدف کمی/کیفی")
    description = models.TextField(verbose_name="شرح")
    description_hidden = models.TextField(verbose_name="شرح مخفی", null=True, blank=True)
    agreement = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, verbose_name="توافق")
    indicators = models.ForeignKey(Indicators, on_delete=models.CASCADE, verbose_name="شاخص")
    assessment = (
        ('O', 'فرصت بهبود'),
        ('S', 'قوت'),
    )
    assessment_type = models.CharField(max_length=1, choices=assessment, null=True, verbose_name="ارزیابی")
    is_open_agreement = models.BooleanField(default=True, null=True, verbose_name="آیا توافق باز است؟")
    type_status_like_dislike = (
        ('L', 'تایید'),
        ('D', 'عدم تایید')
    )
    like_dislike = models.CharField(max_length=1, choices=type_status_like_dislike, null=True, blank=True,
                                    verbose_name='وضعیت تایید')
    be_seen = models.BooleanField(default=False, verbose_name='آیا ارزیابی شونده مشاهده کرده است؟')

    def __str__(self):
        return self.type_report


class Feedback_sessions(models.Model):
    class Meta:
        verbose_name = "جلسات بازخورد"
        verbose_name_plural = "جلسات بازخورد"

    limit_assessor = models.Q(assessor=True)
    assessor = models.ForeignKey(Account, limit_choices_to=limit_assessor, on_delete=models.CASCADE,
                                 related_name="assessor_feedback_sessions",
                                 verbose_name="ارزیابی کننده")
    # limit_be_evaluated = models.Q(be_evaluated__assessor__id=1)
    be_evaluated = models.ForeignKey(Account, on_delete=models.CASCADE,  # limit_choices_to=limit_be_evaluated,
                                     related_name="to_be_evaluated_feedback_sessions", verbose_name="ارزیابی شونده")
    date_report = jmodels.jDateField(verbose_name="تاریخ")
    description = models.TextField(verbose_name="توضیحات")
    description_hidden = models.TextField(verbose_name="توضیحات مخفی", blank=True, null=True)

    def __str__(self):
        return self.be_evaluated.first_name + " " + self.be_evaluated.last_name


class Eval_Report(models.Model):
    class Meta:
        verbose_name = "گزارش های ارزیابی"
        verbose_name_plural = "گزارش های ارزیابی"

    season_name = (
        ('B', 'بهار'),
        ('T', 'تابستان'),
        ('P', 'پاییز'),
        ('Z', 'زمستان')
    )
    season = models.CharField(max_length=1, choices=season_name, verbose_name='فصل')
    year = models.IntegerField(verbose_name="سال")
    limit_assessor = models.Q(assessor=True)
    assessor = models.ForeignKey(Account, limit_choices_to=limit_assessor, on_delete=models.CASCADE,
                                 related_name="assessor_evaluation",
                                 verbose_name="ارزیابی کننده")
    be_evaluated = models.ForeignKey(Account, on_delete=models.CASCADE,
                                     related_name="to_be_evaluated_evaluation", verbose_name="ارزیابی شونده")
    evaluations = models.ManyToManyField(Evaluation, verbose_name="گزارش", blank=True)
    display = models.BooleanField(default=False, verbose_name='آیا گزارش برای ارزیابی شونده نمایش داده شود؟')

    def get_score(self):
        score = 0
        axes_waight = {}
        for eval in self.evaluations.all():
            if eval.indicators.axes.name not in axes_waight:
                axes_waight[eval.indicators.axes.name] = eval.indicators.weight
            else:
                axes_waight[eval.indicators.axes.name] = axes_waight[eval.indicators.axes.name] + eval.indicators.weight

        for eval in self.evaluations.all():
            score += ((eval.indicators.weight * eval.indicators.axes.score * eval.items_evaluation.score) / (
                    7 * axes_waight[eval.indicators.axes.name]))
        return round(score, 2)

    def __str__(self):
        return self.be_evaluated.first_name + " " + self.be_evaluated.last_name


class QuestionForFeedbackSessions(models.Model):
    class Meta:
        verbose_name = "سوالات ارزیابی جلسات بازخورد"
        verbose_name_plural = "سوالات ارزیابی جلسات بازخورد"

    questions = models.TextField(verbose_name='سوال')

    def __str__(self):
        return self.questions


class EvaluationQuestionForFeedbackSessions(models.Model):
    question = models.ForeignKey(QuestionForFeedbackSessions, on_delete=models.CASCADE, verbose_name='سوال')
    score = models.IntegerField(verbose_name='امتیاز')
    description = models.TextField(verbose_name='توضیحات', null=True, blank=True)


class EvaluationForFeedbackSessions(models.Model):
    class Meta:
        verbose_name = "گزارش های ارزیابی جلسات بازخورد"
        verbose_name_plural = "گزارش های ارزیابی جلسات بازخورد"

    questions = models.ManyToManyField(EvaluationQuestionForFeedbackSessions, verbose_name='ایتم های ارزیابی')
    be_evaluated = models.ForeignKey(Account, on_delete=models.CASCADE,
                                     related_name="to_be_evaluated_evaluation_for_feedback_sessions",
                                     verbose_name="ارزیابی شونده")
    feedback_session = models.ForeignKey(Feedback_sessions, on_delete=models.CASCADE, verbose_name='جلسه ی ارزیابی')

    def get_score(self):
        score = 0
        all_questions = self.questions.all()
        for q in all_questions:
            score += q.score
        score = score / len(all_questions)
        return round(score, 2)
