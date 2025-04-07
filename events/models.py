from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
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


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    profile_data = models.JSONField(default=dict, blank=True)
    preferences = models.JSONField(default=dict, blank=True)
    location = models.ForeignKey('Location', on_delete=models.SET_NULL, null=True, blank=False)
    availability = models.JSONField(default=dict, blank=True)

    ROLE_CHOICES = [
        ('user', 'User'),
        ('organizer', 'Organizer'),
        ('admin', 'Admin'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()


class Location(models.Model):
    name = models.CharField(max_length=255, unique=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class EventCategory(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    datetime = models.DateTimeField()
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    category = models.ForeignKey(EventCategory, on_delete=models.SET_NULL, null=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    capacity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']


class EventImage(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='events/')
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.is_primary:
            EventImage.objects.filter(event=self.event).update(is_primary=False)
        super().save(*args, **kwargs)


class RSVP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    STATUS_CHOICES = [
        ('attending', 'Attending'),
        ('maybe', 'Maybe'),
        ('declined', 'Declined'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)


class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=True, blank=True)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    TYPE_CHOICES = [
        ('reminder', 'Reminder'),
        ('message', 'Message'),
        ('update', 'Update'),
    ]
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)


class Contact(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField()
    send_at = models.DateTimeField(auto_now_add=True)

class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    subscribe_at = models.DateTimeField(auto_now_add=True)
