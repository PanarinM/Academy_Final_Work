from __future__ import unicode_literals

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.core.exceptions import ValidationError

from utils import get_file_path


def validate_phone(value):
    codes = {'039',
             '050',
             '063',
             '066',
             '067',
             '068',
             '091',
             '092',
             '093',
             '094',
             '095',
             '096',
             '097',
             '098',
             '099'}
    if str(value)[:3] not in codes or len(value) != 10:
        raise ValidationError('%(value)s is not a valid phone number', params={'value': value},)


class UserManager(BaseUserManager):
    def create_user(self, username, email, phone, password=None):
        if not username:
            raise ValueError('Users should have username')

        user = self.model(email=self.normalize_email(email), username=username, phone=phone)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, phone, password):
        user = self.create_user(
            username,
            email,
            phone,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    username = models.CharField(max_length=40, unique=True, null=False)
    firstname = models.CharField(max_length=40)
    lastname = models.CharField(max_length=40)
    email = models.EmailField()
    phone = models.CharField(max_length=10, null=True, blank=True, validators=[validate_phone])
    birthday = models.DateField(null=True, blank=True)
    registered = models.DateTimeField(auto_now_add=True)
    avatar = models.ImageField(upload_to=get_file_path, default='/user/default_user.png')
    country = models.CharField(max_length=30, null=True, blank=True)
    city = models.CharField(max_length=30, null=True, blank=True)
    street = models.CharField(max_length=30, null=True, blank=True)
    house = models.CharField(max_length=30, null=True, blank=True)
    is_admin = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'phone']

    objects = UserManager()

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin
