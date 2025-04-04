from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EventViewSet, RSVPViewSet, UserRegistrationView, matched_events, EventCategoryViewSet, ContactViewSet

router = DefaultRouter()
router.register(r'events', EventViewSet)
router.register(r'rsvps', RSVPViewSet)
router.register(r'categories', EventCategoryViewSet)
router.register(r'contacts', ContactViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('matched-events/', matched_events, name='matched-events'),
]