from django.http import HttpResponse
from .models import (
    RequestLog,
    RequestLogHistory,
)
from datetime import datetime, timedelta

def get_client_username(request):
	username = request.user.username
	if username is None or username = '':
		username = request.META.get('REMOTE_ADDR', '')
    return username


def get_request_url(request):
    return request.META.get('PATH_INFO', '')

def validate_inputs(**fields):
	if 'limit' in fields:
		if not isinstance(fields['limit'], int):
			raise ValueError(
				"limit: invalid input type 'Expected: int'")

	if 'duration' in fields:
		if not isinstance(duration, timedelta):
			raise ValueError(
				"duration must be an object of datetime.timedelta")

	if restrict_super_user in fields:
		if not isinstance(restrict_super_user, bool):
			raise ValueError(
				"restrict_super_user: invalid input type 'Expected: bool'")


def is_request_count_exceeding(request, limit=1000, duration=timedelta(hours=1), restrict_super_user=True):
	if not restrict_super_user:
		return False

	username = get_client_username(request)
	req_url = get_request_url(request)
	req_count = RequestLogHistory.objects.filter(
		user = username,
		request_url = req_url,
		request_time__gte = datetime.now() - duration
	).count()

	if req_count > limit: 
		return True
	req_his = RequestLogHistory.objects.create(
		user = username,
		request_url = req_url,
	)

	return False
	

def is_request_restricted(request, limit=1000, duration=timedelta(days=1), restrict_super_user=True):
	request_time = datetime.now()
	restrict_req = False
	if not restrict_super_user:
		return restrict_req

	username = get_client_username(request)
	req_url = get_request_url(request)

	try:
		req_log = RequestLog.objects.get(
			user = username, request_url = req_url
		)
	except RequestLog.DoesNotExist:
		req_log = RequestLog(
			user = username, request_url = req_url
			first_attempt = request_time, req_count = 1
		)

	if req_log.req_count > limit:
		if request_time - req_log.first_attempt < duration:
			restrict_req = True

	if req_log.first_attempt - duration > request_time:
		req_log.first_attempt = request_time

	req_log.save()
	return restrict_req

