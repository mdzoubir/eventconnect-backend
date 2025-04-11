from django.db import IntegrityError
from django.db.models.aggregates import Count
from django.utils import timezone
from rest_framework import viewsets, generics, mixins
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from .models import Event, RSVP, User, EventCategory, Contact, Subscriber
from .permissions import IsOrganizerReadOnly
from .serializers import EventListSerializer, EventSerializer, UserRegistrationSerializer, RSVPSerializer, \
    EventCategorySerializer, ContactSerializer, SubscriberSerializer

from .utils import match_events_to_user


#  Custom pagination
class EventPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    pagination_class = EventPagination

    def get_queryset(self):
        queryset = Event.objects.all()
        ordering = self.request.query_params.get('sorting')
        category_name = self.request.query_params.get('event_type')

        if category_name:
            queryset = queryset.filter(category__name__iexact=category_name)

        if ordering == 'recent':
            queryset = queryset.order_by('-created_at')
        elif ordering == 'upcoming':
            now = timezone.now()
            queryset = queryset.filter(datetime__gte=now).order_by('datetime')

        return queryset

    def get_serializer_class(self):
        if self.action == 'list':
            return EventListSerializer
        return EventSerializer

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response.data['total_pages'] = (response.data['count'] // self.pagination_class.page_size) + 1
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
        instance.delete()


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
