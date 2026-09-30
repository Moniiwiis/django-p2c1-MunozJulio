from core.access import get_actor_context


def actor_access(request):
    return get_actor_context(request.user)