from datetime import datetime

from django.db import models
from pytz import timezone


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