from django.db import transaction
from django.utils import timezone
from rest_framework import serializers
from .models import Event, User, RSVP, EventCategory, EventImage, Location, Contact


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['id', 'name', 'latitude', 'longitude', 'address']
        # Remove the uniqueness validation from the serializer
        extra_kwargs = {
            'name': {'validators': []}  # Remove all validators including UniqueValidator
        }


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    location = LocationSerializer(required=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'preferences', 'location', 'role')

    def create(self, validated_data):
        location_data = validated_data.pop('location')

        with transaction.atomic():  # Ensures both are saved together
            location, created = Location.objects.get_or_create(name=location_data['name'])

            # If location exists but has different details, update it
            if not created:
                location.latitude = location_data.get('latitude', location.latitude)
                location.longitude = location_data.get('longitude', location.longitude)
                location.address = location_data.get('address', location.address)
                location.save()

            validated_data['location'] = location
            user = User.objects.create_user(**validated_data)

        return user

class EventImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventImage
        fields = ['id', 'image', 'is_primary']


class EventSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=EventCategory.objects.all(), allow_null=True)
    location = LocationSerializer()
    images = EventImageSerializer(many=True, required=False)
    creator = serializers.ReadOnlyField(source='creator.username')

    class Meta:
        model = Event
        fields = ['id', 'title', 'description', 'datetime', 'location', 'creator', 'category', 'images', 'capacity', 'price']
        read_only_fields = ('creator',)

    def validate(self, data):
        if data['datetime'] < timezone.now():
            raise serializers.ValidationError({"date": "Event date cannot be in the past."})
        return data

    def create(self, validated_data):
        images_data = self.context['request'].FILES.getlist('images')
        primary_image = self.context['request'].data.get('primary_image')

        location_data = validated_data.pop('location')
        location, _ = Location.objects.get_or_create(**location_data)

        # Create event
        event = Event.objects.create(location=location, **validated_data)

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
        fields = ['username', 'preferences', 'location']


class RSVPSerializer(serializers.ModelSerializer):
    class Meta:
        model = RSVP
        fields = '__all__'
        read_only_fields = ('user', 'timestamp')


class EventCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = EventCategory
        fields = ["name"]


class EventListSerializer(serializers.ModelSerializer):
    category = EventCategorySerializer()
    primary_image = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = ['id', 'title', 'description', 'datetime', 'location', 'creator', 'category', 'primary_image']

    def get_primary_image(self, obj):
        primary_image = obj.images.filter(is_primary=True).first()
        if primary_image:
            return EventImageSerializer(primary_image).data
        return None


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = '__all__'