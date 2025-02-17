from django.utils import timezone
from rest_framework import viewsets, generics, serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action

from .models import Event, RSVP, User, EventCategory
from .serializers import EventListSerializer, EventSerializer, UserRegistrationSerializer, RSVPSerializer, EventCategorySerializer

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
        ordering = self.request.query_params.get('ordering')

        if ordering == 'recent':
            return queryset.order_by('-created_at')
        elif ordering == 'upcoming':
            now = timezone.now()
            return queryset.filter(date__gte=now).order_by('date')

        print(queryset)
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
        serializer.save(organizer=user)

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

        if event.date < timezone.now():
            raise ValidationError({"error": "You cannot RSVP for an event that has already passed."})

        if RSVP.objects.filter(user=user, event=event).exists():
            raise ValidationError({"error": "You have already RSVP'd for this event."})

        serializer.save(user=user, event=event)


class EventCategoryViewSet(viewsets.ModelViewSet):
    queryset = EventCategory.objects.all()
    serializer_class = EventCategorySerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def matched_events(request):
    user = request.user
    events = Event.objects.all()
    matched = match_events_to_user(user, events)
    serializer = EventSerializer(matched, many=True)
    return Response(serializer.data)


