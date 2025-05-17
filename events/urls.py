from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EventViewSet, RSVPViewSet, UserRegistrationView, matched_events, EventCategoryViewSet, \
    ContactViewSet, SubscriberViewSet, UsersViewSet,  TicketViewSet, \
     ReviewViewSet, NotificationViewSet, UserProfileView, EventStatisticsView

router = DefaultRouter()
router.register(r'users', UsersViewSet)
router.register(r'events', EventViewSet)
router.register(r'rsvps', RSVPViewSet)
router.register(r'event-categories', EventCategoryViewSet)
router.register(r'contacts', ContactViewSet)
router.register(r'subscribers', SubscriberViewSet)
router.register(r'tickets', TicketViewSet)
router.register(r'reviews', ReviewViewSet)
router.register(r'notifications', NotificationViewSet)

urlpatterns = [
    path('v1/', include(router.urls)),
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('matched-events/', matched_events, name='matched-events'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('events/<int:pk>/statistics/', EventStatisticsView.as_view(), name='event-statistics'),
]