from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EventViewSet, RSVPViewSet, UserRegistrationView, matched_events, EventCategoryViewSet, \
    ContactViewSet, SubscriberViewSet, UsersViewSet

router = DefaultRouter()
router.register(r'users', UsersViewSet)
router.register(r'events', EventViewSet)
router.register(r'rsvps', RSVPViewSet)
router.register(r'event-categories', EventCategoryViewSet)
router.register(r'contacts', ContactViewSet)
router.register(r'subscribers', SubscriberViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('matched-events/', matched_events, name='matched-events'),
]