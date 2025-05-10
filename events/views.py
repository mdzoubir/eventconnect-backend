import math

from django.db import IntegrityError
from django.db.models.aggregates import Count
from django.utils import timezone
from rest_framework import viewsets, generics, mixins, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .models import Event, RSVP, User, EventCategory, Contact, Subscriber
from .permissions import IsOrganizerReadOnly, IsAdminOrOrganizer, IsOwnerOrAllowed
from .serializers import EventListSerializer, EventSerializer, UserRegistrationSerializer, RSVPSerializer, \
    EventCategorySerializer, ContactSerializer, SubscriberSerializer, UserSerializer
from .utils import match_events_to_user


#  Custom pagination
class EventPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'create':
            # Anyone can create a user (register)
            permission_classes = [permissions.AllowAny]
        elif self.action in ['update', 'partial_update', 'destroy']:
            # Only admins or the user themselves can update/delete
            permission_classes = [permissions.IsAuthenticated, IsOwnerOrAllowed]
        else:
            # For list and retrieve, require admin permissions
            permission_classes = [IsAdminOrOrganizer]
        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        # This will run all validators and raise validation errors if any
        serializer.is_valid(raise_exception=True)

        # Additional pre-save validation if needed
        try:
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        # Additional validation for updates
        if 'role' in serializer.validated_data and not request.user.role in ['admin', 'organizer']:
            return Response(
                {"role": "You don't have permission to change roles."},
                status=status.HTTP_403_FORBIDDEN
            )

        self.perform_update(serializer)
        return Response(serializer.data)

    def get_queryset(self):
        queryset = User.objects.all()
        role = self.request.query_params.get('role')
        if role:
            queryset = queryset.filter(role__iexact=role).exclude(status='deleted')
        return queryset




class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    pagination_class = EventPagination

    def get_queryset(self):
        ordering = self.request.query_params.get('sorting')
        category = self.request.query_params.get('event_type')
        return Event.objects.active().filter_by_category(category).order_events(ordering)

    def get_serializer_class(self):
        if self.action == 'list':
            return EventListSerializer
        return EventSerializer

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response.data['total_pages'] = math.ceil(response.data['count'] / self.pagination_class.page_size)
        return response

    def get_permissions(self):
        if self.action == 'list':
            return [AllowAny()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        user = self.request.user
        if user.role != 'organizer':
            raise PermissionDenied(
                "Only organizers can create events."
            )
        serializer.save(creator=user)

    def perform_update(self, serializer):
        user = self.request.user
        if user.role != 'organizer':
            raise PermissionDenied('Only organizers can update events.')
        serializer.save()

    def perform_destroy(self, instance):
        user = self.request.user
        if user.role != 'organizer':
            raise PermissionDenied('Only organizers can delete events.')
        instance.is_deleted = True
        instance.save()


class EventCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = EventCategory.objects.annotate(
        event_count=Count('event')
    ).filter(event_count__gt=0)

    serializer_class = EventCategorySerializer
    permission_classes = [AllowAny]


class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer


class RSVPViewSet(viewsets.ModelViewSet):
    queryset = RSVP.objects.all()
    serializer_class = RSVPSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        event = serializer.validated_data['event']

        if event.datetime < timezone.now():
            raise ValidationError({"error": "You cannot RSVP for an event that has already passed."})

        if RSVP.objects.filter(user=user, event=event).exists():
            raise ValidationError({"error": "You have already RSVP'd for this event."})

        serializer.save(user=user, event=event)




class ContactViewSet(mixins.CreateModelMixin,
                     mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     viewsets.GenericViewSet):  # Note: no UpdateModelMixin or DestroyModelMixin
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer

    def get_permissions(self):
        if self.action == 'create':
            # Anyone can create a contact message
            return [AllowAny()]
        # Only organizers can list or retrieve
        return [IsOrganizerReadOnly()]


class SubscriberViewSet(mixins.CreateModelMixin,
                        mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    serializer_class = SubscriberSerializer
    queryset = Subscriber.objects.all()

    def get_permissions(self):
        if self.action == 'create':
            # Anyone can create a contact message
            return [AllowAny()]
        # Only organizers can list or retrieve
        return [IsOrganizerReadOnly()]

    def perform_create(self, serializer):
        try:
            serializer.save()  # Attempt to save the new subscriber
        except IntegrityError:
            raise ValidationError({"email": "This email address is already subscribed."})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def matched_events(request):
    user = request.user
    events = Event.objects.all()
    matched = match_events_to_user(user, events)
    serializer = EventSerializer(matched, many=True)
    return Response(serializer.data)
