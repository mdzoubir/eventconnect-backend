from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from rest_framework.exceptions import ValidationError


# Create your models here.
class User(AbstractUser):
    ROLE_CHOICES = (
        ('organizer', 'Organizer'),
        ('participant', 'Participant'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='participant')
    interests = models.TextField()
    location = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.username} ({self.role})"


class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateTimeField()
    location = models.CharField(max_length=255)
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="organized_events")
    category = models.ForeignKey('EventCategory', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.title


class EventCategory(models.Model):
    name = models.CharField(max_length=100)


class RSVP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'event'], name='unique_rsvp')
        ]
