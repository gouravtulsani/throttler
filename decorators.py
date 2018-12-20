from .utils import (
	get_client_username,
	get_request_url,
	validate_inputs,
	is_request_too_frequent,
	is_request_restricted,
)
from django.http import HttpResponse
from datetime import datetime, timedelta


def restrict_request(limit=1000, duration=timedelta(days=1), restrict_super_user=True, resp_msg=None):
	validate_inputs(
		limit=limit, duration=duration, restrict_super_user=restrict_super_user
	)
	if resp_msg is None:
		resp_msg='request limit exceed'
	def view_restrict(function):
		def wrapper(request, *args, **kwargs):
			if not restrict_super_user and request.user.is_superuser:
				return function(request, *args, **kwargs)

			if is_request_restricted(request, limit=limit, duration=duration, restrict_super_user=restrict_super_user):

				return HttpResponse(
					resp_msg, content_type='application/json', status=429)

			return function(request, *args, **kwargs)
		return wrapper
	return view_restrict


def restrict_frequent_requests(duration_bw_reqs=timedelta(days=1), restrict_super_user=True):
	validate_inputs(
		duration=duration_bw_reqs, restrict_super_user=restrict_super_user
	)
	def view_restrict(function):
		def wrapper(request, *args, **kwargs):
			if not restrict_super_user and request.user.is_superuser:
				return function(request, *args, **kwargs)

			if is_request_too_frequent(request, duration=duration_bw_reqs, restrict_super_user=restrict_super_user):
				resp={'Too frequent attempt: dropping request'}
				return HttpResponse(
					resp, content_type='application/json', status=429)

			return function(request, *args, **kwargs)
		return wrapper
	return view_restrict
