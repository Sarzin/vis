import datetime

from django.contrib.auth import user_logged_in
from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser,
    PermissionsMixin)

from django_jalali.db import models as jmodels
from jalali_date import datetime2jalali, date2jalali


class Unit(models.Model):
    class Meta:
        verbose_name = ' واحد  سازمانی'
        verbose_name_plural = '  واحدهای  سازمانی'

    name = models.CharField(max_length=100, verbose_name="نام واحد")

    def __str__(self):
        return self.name

    # def create_user(self, password, **extra_fields):
    #     """
    #     Create and save a User with the given email and password.
    #     """
    #     # if not email:
    #     #     raise ValueError('The Email must be set')
    #     # email = self.normalize_email(email)
    #     user = self.model(**extra_fields)
    #     user.set_password(password)
    #     user.save()
    #     return user


class UserManager(BaseUserManager):
    def create_user(self, username, password=None):
        """
        Creates and saves a User with the given email and password.
        """
        if not username:
            raise ValueError('Users must have an username address')
        user = self.model(
            username=(username),
        )
        user.set_password(password)
        user.save()
        return user

    def create_staffuser(self, username, password):
        """
        Creates and saves a staff user with the given email and password.
        """
        user = self.create_user(
            username,
            password=password,
        )
        # user.staff = True
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(
            username,
            password=password,
        )
        # user.staff = True
        user.admin = True
        user.assessor = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class Account(AbstractBaseUser, PermissionsMixin):
    class Meta:
        verbose_name = 'حساب کاربری'
        verbose_name_plural = ' حساب های کاربری'

    picture = models.FileField(verbose_name='تصوير', upload_to='user_picture/', default='user_picture/default.png',
                               blank=True)
    first_name = models.CharField(max_length=60, verbose_name='نام', blank=True)
    last_name = models.CharField(max_length=60, verbose_name='نام خانوادگی', blank=True)
    username = models.CharField(max_length=60, verbose_name='نام کاربری', null=True, blank=True, unique=True, )
    phone_number = models.BigIntegerField(default=0, verbose_name='شماره تماس', blank=True, null=True)
    Personnel_Code = models.BigIntegerField(default=0, verbose_name='کد پرسنلی', blank=True, null=True)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, verbose_name='واحد سازمانی', null=True, blank=True)
    email = models.EmailField(
        verbose_name='ایمیل',
        max_length=255,
        unique=True,
        blank=True,
        null=True
    )
    job_side = models.CharField(max_length=60, verbose_name='عنوان شغلی', blank=True, null=True)
    is_active = models.BooleanField(default=True, verbose_name='آیا فعال است؟')
    # staff = models.BooleanField(default=True, verbose_name='')
    assessor = models.BooleanField(default=False, verbose_name='آیا ارزیابی کننده است؟')  # a admin user; non super-user
    admin = models.BooleanField(default=False, verbose_name='آیا مدیر است؟')  # a superuser
    join_date = jmodels.jDateField(auto_now_add=True, verbose_name="تاریخ عضویت")

    # notice the absence of a "Password field", that is built in.

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []  # Email & Password are required by default.

    def get_full_name(self):
        return self.first_name + ' ' + self.last_name

    def get_jalali_date(self):
        return datetime2jalali(self.join_date)

    # def save(self, *args, **kwargs):
    #     self.fullname = self.first_name + ' ' + self.last_name
    #     super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.first_name} {self.last_name} - {self.unit} - {self.Personnel_Code}'

    # def has_perm(self, perm, obj=None):
    #     "Does the user have a specific permission?"
    #     # Simplest possible answer: Yes, always
    #     return True
    #
    # def has_module_perms(self, app_label):
    #     "Does the user have permissions to view the app `app_label`?"
    #     # Simplest possible answer: Yes, always
    #     return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        return self.admin

    @property
    def is_admin(self):
        "Is the user a admin member?"
        return self.admin

    def update_last_login(sender, user, **kwargs):
        """
        A signal receiver which updates the last_login date for
        the user logging in.
        """
        user.last_login = datetime.datetime.now()
        user.save(update_fields=['last_login'])

    user_logged_in.connect(update_last_login)

    objects = UserManager()


class staff_assessor(models.Model):
    class Meta:
        verbose_name = 'انتساب ارزیابی شونده'
        verbose_name_plural = "انتساب ارزیابی شونده"

    limit_assessor = models.Q(assessor=True)
    assessor = models.ForeignKey(Account, limit_choices_to=limit_assessor, on_delete=models.CASCADE,
                                 related_name="assessor_of_staff",
                                 verbose_name='ارزیابی کننده')
    staff = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='be_evaluated',
                              verbose_name='ارزیابی شونده')
