from django.core.exceptions import PermissionDenied
from .models import Study

def check_if_user_is_author(function):
    def wrap(request, *args, **kwargs):
        study = Study.objects.get(pk=kwargs['pk'])
        if study.user == request.user:
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied
    return wrap