from django.conf import settings
from django.http import HttpResponse
from .models import (
    RequestLog,
    RequestLogHistory,
)
from datetime import datetime, timedelta
from django.utils import timezone

def get_client_username(request):
    username = request.user.username
    if username is None or username == '':
        username = request.META.get('REMOTE_ADDR', '')
    return username


def get_request_url(request):
    return request.META.get('PATH_INFO', '')

def request_logger(request):
    username = get_client_username(request)
    req_url = get_request_url(request)

    RequestLogHistory.objects.create(
        user = username,
        request_url = req_url
    )


def validate_inputs(**fields):
    if 'integer' in fields and fields['integer'] is not None:
        if not isinstance(fields['integer'], int):
            raise ValueError(
                "invalid input type 'Expected: int'")

    if 'string' in fields and fields['string'] is not None:
        if not isinstance(fields['string'], str):
            raise ValueError(
                "invalid input type 'Expected: str'")

    if 'datetimedelta' in fields and fields['datetimedelta'] is not None:
        if not isinstance(fields['datetimedelta'], timedelta):
            raise ValueError(
                "must be an object of datetime.timedelta")

    if 'boolean' in fields and fields['boolean'] is not None:
        if not isinstance(fields['boolean'], bool):
            raise ValueError(
                "invalid input type 'Expected: bool'")

    if 'callable' in fields and fields['callable'] is not None:
        if not callable(fields['callable']):
            raise ValueError(
                "invalid input type Expected callable")


def is_request_too_frequent(request, duration=timedelta(seconds=1)):
    request_time = timezone.now()

    username = get_client_username(request)
    req_url = get_request_url(request)

    try:
        req_log = RequestLog.objects.get(
            user = username, request_url = req_url
        )
    except RequestLog.DoesNotExist:
        req_log = RequestLog(
            user = username, request_url = req_url,
            first_attempt = request_time, req_count = 1
        )

    if req_log.last_attempt + duration > request_time: 
        return True

    req_log.save()
    return False
    

def is_request_restricted(request, limit=1000, duration=timedelta(days=1), restrict_super_user=True):
    request_time = timezone.now()
    restricted_req = True
    if not restrict_super_user:
        restricted_req = False

    username = get_client_username(request)
    req_url = get_request_url(request)
        
    if hasattr(settings, 'BLACK_LISTED_USERS'):
        if username in settings.BLACK_LISTED_USERS:
            return restricted_req

    if hasattr(settings, 'WHITE_LISTED_USERS'):
        if username in settings.WHITE_LISTED_USERS:
            restricted_req = False
            return restricted_req

    try:
        req_log = RequestLog.objects.get(
            user = username, request_url = req_url
        )
    except RequestLog.DoesNotExist:
        req_log = RequestLog(
            user = username, request_url = req_url,
            first_attempt = request_time, req_count = 0
        )

    if req_log.req_count < limit and restricted_req:
        restricted_req = False
        req_log.req_count += 1
    else:
        if request_time > req_log.first_attempt + duration and restricted_req:
            restricted_req = False
            req_log.req_count += 1
        
    if req_log.first_attempt + duration < request_time:
        req_log.first_attempt = request_time
        req_log.req_count = 1
        if restricted_req:
            restricted_req = False
            req_log.req_count += 1

    req_log.save()
    return restricted_req

