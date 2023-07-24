from builtins import min

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from accounts.models import Account


class Axes(models.Model):
    class Meta:
        verbose_name = "محور ارزیابی"
        verbose_name_plural = " محور های ارزیابی"

    name = models.CharField(max_length=100, verbose_name='اسم محور')
    score = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(100)], verbose_name='امتیاز محور')

    def __str__(self):
        return f'{self.name}'


class Items_evaluation(models.Model):
    class Meta:
        verbose_name = "گویه های ارزیابی"
        verbose_name_plural = "گویه های ارزیابی"

    name = models.TextField(verbose_name='نام گویه')
    score = models.IntegerField(verbose_name='امتیاز گویه', validators=[MinValueValidator(-7), MaxValueValidator(7)])

    def __str__(self):
        return self.name


class Indicators(models.Model):
    class Meta:
        verbose_name = "شاخص  ارزیابی"
        verbose_name_plural = "شاخص های ارزیابی"

    name = models.CharField(max_length=100, verbose_name='اسم شاخص')
    axes = models.ForeignKey(Axes, on_delete=models.CASCADE, null=True, blank=True, verbose_name='اسم محور')
    items = models.ManyToManyField(Items_evaluation, verbose_name='آیتم های ارزیابی', blank=True)
    limit_assessor = models.Q(assessor=True)
    assessor = models.ForeignKey(Account, limit_choices_to=limit_assessor, on_delete=models.CASCADE, blank=True,
                                 null=True,
                                 related_name="assessor_indicators",
                                 verbose_name="نام ارزیاب")
    # limit_be_evaluated = models.Q(be_evaluated__assessor=assessor)
    be_evaluated = models.ManyToManyField(Account, blank=True,
                                          verbose_name="ارزیابی شونده ها", )
    weight = models.FloatField(verbose_name='وزن شاخص', validators=[MinValueValidator(0), MaxValueValidator(1)])

    def get_items(self):
        return "\n".join([p.name + ' - ' for p in self.items.all()])

    def __str__(self):
        return f'{self.name}'


################################################


class Evaluation(models.Model):
    class Meta:
        verbose_name = "لیست های ارزیابی"
        verbose_name_plural = "لیست های ارزیابی"

    indicators = models.ForeignKey(Indicators, on_delete=models.CASCADE, verbose_name="شاخص")
    items_evaluation = models.ForeignKey(Items_evaluation, on_delete=models.CASCADE, verbose_name="گویه", null=True,
                                         blank=True)

    def __str__(self):
        return f'{self.indicators} - {self.items_evaluation}'
