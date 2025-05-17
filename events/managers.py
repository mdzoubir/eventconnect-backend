from datetime import datetime
from django.contrib.auth.base_user import BaseUserManager

from django.db import models



class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)
    
class EventQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_deleted=False)

    def filter_by_category(self, category_name):
        if category_name:
            return self.filter(category__name__iexact=category_name)
        return self

    def order_events(self, ordering):
        now = datetime.now()
        if ordering == 'recent':
            return self.order_by('-created_at')
        elif ordering == 'upcoming':
            return self.filter(start_datetime__gte=now).order_by('start_datetime')
        return self