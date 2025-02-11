from django.utils import timezone
from rest_framework import serializers
from .models import Event, User, RSVP, EventCategory


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'interests', 'location', 'role')

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class EventSerializer(serializers.ModelSerializer):
    category = serializers.CharField()


    class Meta:
        model = Event
        fields = '__all__'
        read_only_fields = ('organizer',)

    def validate(self, data):
        # for event date
        if data['date'] < timezone.now():
            raise serializers.ValidationError({"date": "Event date cannot be in the past."})

        # for event category
        category_name = data.get('category')
        if category_name:
            category, created = EventCategory.objects.get_or_create(name=category_name)
            data['category'] = category

        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'interests', 'location']


class RSVPSerializer(serializers.ModelSerializer):
    class Meta:
        model = RSVP
        fields = '__all__'
        read_only_fields = ('user',)


class EventCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = EventCategory
        fields = '__all__'
