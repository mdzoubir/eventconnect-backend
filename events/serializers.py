import json

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator
from django.db import transaction
from django.utils import timezone
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Event, User, RSVP, EventCategory, EventImage, Location, Contact, Subscriber, EventTag, Ticket, Transaction, Waitlist, Review, Notification


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['id', 'name', 'latitude', 'longitude', 'address', 'country', 'city', 'postal_code']
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
        fields = ['image', 'is_primary']


class EventTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventTag
        fields = ['id', 'name', 'slug']

class EventSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=EventCategory.objects.all(), allow_null=True)
    location = LocationSerializer()
    images = EventImageSerializer(many=True, required=False, read_only=True)
    creator = serializers.ReadOnlyField(source='creator.email')
    tags = EventTagSerializer(many=True, required=False)
    tickets = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = ['id', 'title', 'description', 'start_datetime', 'end_datetime',
                 'location', 'category', 'creator', 'capacity', 'price',
                 'minimum_age', 'is_deleted', 'status', 'created_at',
                 'updated_at', 'images', 'tags', 'tickets']
        read_only_fields = ('creator', 'is_deleted')

    def get_tickets(self, obj):
        return TicketSerializer(obj.tickets.filter(is_active=True), many=True).data

    def validate(self, data):
        # Existing validation
        if data['start_datetime'] < timezone.now():
            raise serializers.ValidationError({"start_datetime": "Event start date cannot be in the past."})
        if data['end_datetime'] < data['start_datetime']:
            raise serializers.ValidationError({"end_datetime": "Event end date must be after start date."})
        return data

    def create(self, validated_data):
        request = self.context['request']
        images_data = request.FILES.getlist('images')
        primary_index = request.data.get('primary_image')

        location_data = validated_data.pop('location')
        location, _ = Location.objects.get_or_create(**location_data)
        validated_data['location'] = location

        event = Event.objects.create(**validated_data)

        for index, image_file in enumerate(images_data):
            is_primary = str(index) == str(primary_index)
            EventImage.objects.create(event=event, image=image_file, is_primary=is_primary)

        return event


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        validators=[MinLengthValidator(8)]
    )

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'date_joined',
                  'profile_data', 'preferences', 'role', 'status',
                  'password']
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': False},
            'last_name': {'required': False},
        }

    def validate_email(self, value):
        """Validate email format and uniqueness"""
        # Check if email already exists (case insensitive)
        normalized_email = value.lower()

        # For update operations, exclude the current instance
        if self.instance and self.instance.email.lower() == normalized_email:
            return value

        if User.objects.filter(email__iexact=normalized_email).exists():
            raise serializers.ValidationError("A user with this email already exists.")

        # Additional email validation if needed
        domain = value.split('@')[1] if '@' in value else ''
        if domain.endswith('.test') or domain.endswith('.example'):
            raise serializers.ValidationError("Email domain not allowed.")

        return value

    def validate_password(self, value):
        """Validate password strength"""
        try:
            # Use Django's built-in password validators
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(list(e.messages))

        # Custom password validation rules
        if value.lower().find('password') != -1:
            raise serializers.ValidationError("Password cannot contain the word 'password'.")

        return value

    def validate(self, data):
        """Validate the entire data set"""
        # Status-specific validations
        if 'status' in data and data['status'] == 'deleted':
            if 'role' in data and data['role'] == 'admin':
                raise serializers.ValidationError({"status": "Admin accounts cannot be marked as deleted."})

        return data

    def create(self, validated_data):
        # Hash the password before saving the user
        password = validated_data.pop('password', None)
        user = User(**validated_data)

        if password:
            user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        # Hash the password before saving if it is provided
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)
        instance.save()
        return instance



class TicketSerializer(serializers.ModelSerializer):
    available = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Ticket
        fields = ['id', 'event', 'name', 'description', 'price', 'quantity',
                 'remaining', 'sale_start', 'sale_end', 'is_active', 'available']
    
    def validate(self, data):
        if data['sale_end'] < data['sale_start']:
            raise serializers.ValidationError({"sale_end": "Sale end date must be after sale start date."})
        if data['quantity'] < 1:
            raise serializers.ValidationError({"quantity": "Quantity must be at least 1."})
        return data



class RSVPSerializer(serializers.ModelSerializer):
    ticket_details = TicketSerializer(source='ticket', read_only=True)

    class Meta:
        model = RSVP
        fields = ['id', 'user', 'event', 'status', 'timestamp', 'ticket',
                 'ticket_details', 'quantity', 'notes', 'check_in_time',
                 'check_in_status']
        read_only_fields = ('user', 'timestamp', 'check_in_time', 'check_in_status')

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("Quantity must be at least 1.")
        return value


class EventCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = EventCategory
        fields = ["id", "name"]


class EventListSerializer(serializers.ModelSerializer):
    category = EventCategorySerializer()
    primary_image = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = ['id', 'title', 'description', 'start_datetime', 'end_datetime', 'location', 'creator', 'category',
                  'primary_image']

    def get_primary_image(self, obj):
        primary_image = obj.images.filter(is_primary=True).first()
        if primary_image:
            return EventImageSerializer(primary_image).data
        return None


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = '__all__'


class SubscriberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscriber
        fields = ['email']


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['role'] = user.role  # assuming you have a role field in your user model

        return token


class TransactionSerializer(serializers.ModelSerializer):
    ticket_details = TicketSerializer(source='ticket', read_only=True)
    
    class Meta:
        model = Transaction
        fields = ['id', 'user', 'ticket', 'ticket_details', 'amount',
                 'payment_method', 'transaction_id', 'status', 'created_at']
        read_only_fields = ('user', 'transaction_id', 'created_at')

    def validate(self, data):
        ticket = data['ticket']
        if ticket.remaining < 1:
            raise serializers.ValidationError({"ticket": "This ticket is sold out."})
        if not ticket.is_active:
            raise serializers.ValidationError({"ticket": "This ticket is not available for purchase."})
        return data


class WaitlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Waitlist
        fields = ['id', 'event', 'user', 'joined_at', 'notified', 'notified_at']
        read_only_fields = ('user', 'joined_at', 'notified', 'notified_at')


class ReviewSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source='user', read_only=True)
    
    class Meta:
        model = Review
        fields = ['id', 'user', 'user_details', 'event', 'rating',
                 'comment', 'timestamp']
        read_only_fields = ('user', 'timestamp')

    def validate_rating(self, value):
        if not (1 <= value <= 5):
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'user', 'type', 'content', 'is_read',
                 'timestamp']
        read_only_fields = ('user', 'timestamp')


class EventDetailSerializer(EventSerializer):
    reviews = ReviewSerializer(many=True, read_only=True)
    waitlist_count = serializers.IntegerField(read_only=True)
    is_sold_out = serializers.BooleanField(read_only=True)
    
    class Meta(EventSerializer.Meta):
        fields = EventSerializer.Meta.fields + ['reviews', 'waitlist_count', 'is_sold_out']




