from .models import ActivityLog


def create_log(user, action):

    ActivityLog.objects.create(
        user=user,
        action=action
    )