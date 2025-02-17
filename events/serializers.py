from django.utils import timezone
from rest_framework import serializers
from .models import Event, User, RSVP, EventCategory, EventImage


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'interests', 'location', 'role')

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class EventImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventImage
        fields = ['id', 'image', 'is_primary']

class EventSerializer(serializers.ModelSerializer):
    category = serializers.CharField()
    images = EventImageSerializer(many=True, required=False)

    class Meta:
        model = Event
        fields = ['id', 'title', 'description', 'date', 'location', 'organizer', 'category', 'images']
        read_only_fields = ('organizer',)

    def validate(self, data):
        if data['date'] < timezone.now():
            raise serializers.ValidationError({"date": "Event date cannot be in the past."})

        category_name = data.get('category')
        if category_name:
            category, created = EventCategory.objects.get_or_create(name=category_name)
            data['category'] = category

        return data
    
    def create(self, validated_data):
        images_data = self.context['request'].FILES.getlist('images')
        primary_image = self.context['request'].data.get('primary_image')

        # Create event
        event = Event.objects.create(**validated_data)

        # Create images
        for index, image_data in enumerate(images_data):
            is_primary = str(index) == str(primary_image)
            EventImage.objects.create(
                event=event,
                image=image_data,
                is_primary=is_primary
            )

        return event

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
        fields = ["name"]


class EventListSerializer(serializers.ModelSerializer):
    category = EventCategorySerializer()
    primary_image = serializers.SerializerMethodField()
    
    class Meta:
        model = Event
        fields = ['id', 'title', 'description', 'date', 'location', 'organizer', 'category', 'primary_image']

    def get_primary_image(self, obj):
        primary_image = obj.images.filter(is_primary=True).first()
        if primary_image:
            return EventImageSerializer(primary_image).data
        return None
