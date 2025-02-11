def match_events_to_user(user, events_queryset):
    user_keywords = set(user.interests.lower().split())
    matching_events = []
    for event in events_queryset:
        event_keywords = set(event.category.lower().split())
        if user_keywords.intersection(event_keywords):
            matching_events.append(event)
    return matching_events