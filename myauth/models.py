from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager, PermissionsMixin)
from django.db import models
from django.utils import timezone

"""
Custom User classes for wgmanager
"""

class CustomUserManager(BaseUserManager):

    def create_user(self, email, first_name, password=None):
        """
        Creates and saves a User with the given email, first name and password.
        """
        now = timezone.now()
        if not email:
            raise ValueError('Email must be supplied.')
        if not first_name:
            raise ValueError('First name must be set.')
        email = BaseUserManager.normalize_email(email)

        user = self.model(email=email, first_name=first_name,
                          is_active=False, is_admin=False,
                          last_login=now, date_joined=now)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, password):
        u = self.create_user(email, first_name, password=password)
        u.is_admin = True
        u.is_active = True
        u.save(using=self._db)
        return u


class MyUser(AbstractBaseUser):
    email = models.EmailField(unique=True, max_length=255)

    first_name = models.CharField(max_length=30, blank=False)
    last_name = models.CharField(max_length=30, blank=True)

    date_joined = models.DateTimeField(default=timezone.now)
    # last_login defined by abstract base class
    # last_login = models.DateTimeField(default=timezone.now, null=True)

    is_active = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name']


    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        "Returns the short name for the user."
        return self.first_name

    def __str__(self):              # __unicode__ on Python 2
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_perms(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perm(self, app_label):
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        # Simplest possible answer: All admins are staff
        return self.is_admin

    @property
    def is_superuser(self):
        # Simplest possible answer: All admins are staff
        return self.is_admin
