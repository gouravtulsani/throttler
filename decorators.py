from .utils import (
	get_client_username,
	get_request_url,
	validate_inputs,
	is_request_count_exceeding,
	is_request_restricted,
)
from django.http import HttpResponse
from datetime import datetime, timedelta


def restrict_request(limit=1000, duration=timedelta(days=1), restrict_super_user=True):
	validate_inputs(
		limit=limit, duration=duration, restrict_super_user=restrict_super_user
	)
	def view_restrict(function):
		def wrapper(request, *args, **kwargs):
			if not restrict_super_user and request.user.is_superuser:
				return function(request, *args, **kwargs)

			if is_request_restricted(limit=limit, duration=duration, restrict_super_user=restrict_super_user):
				resp={'status': 'request limit exceed'}
				return HttpResponse(
					resp, content_type='application/json', status=429)

			return function(request, *args, **kwargs)
		return wrapper
	return view_restrict


def restrict_request_count(limit=1000, duration=timedelta(days=1), restrict_super_user=True):
	validate_inputs(
		limit=limit, duration=duration, restrict_super_user=restrict_super_user
	)
	def view_restrict(function):
		def wrapper(request, *args, **kwargs):
			if not restrict_super_user and request.user.is_superuser:
				return function(request, *args, **kwargs)

			if is_request_count_exceeding(limit=limit, duration=duration, restrict_super_user=restrict_super_user):
				resp={'status': 'request limit exceed'}
				return HttpResponse(
					resp, content_type='application/json', status=429)

			return function(request, *args, **kwargs)
		return wrapper
	return view_restrict

def ViewRestrict(page, widget):
    if (not isinstance(page, str)) or (not isinstance(widget, str)):
        raise ValueError("args must be strings")
    if page not in role_schema:
        raise ValueError("Key '%s' undefined in schema" % page)
    if widget not in role_schema[page]:
        raise ValueError("Key '%s' undefined in %s object of schema" % (widget, page))
    def view_restrict(function):
        def wrap(request, *args, **kwargs):
            django_timezone.activate(timezone(get_tzinfo({'user_id':request.user.id})))
            if request.user.is_superuser:
                return function(request, *args, **kwargs)

            function_restrict(request.user, page, widget)
            
            return function(request, *args, **kwargs)

        wrap.__doc__ = function.__doc__

        return wrap
    return view_restrict