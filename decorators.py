from .utils import (
    get_client_username,
    get_request_url,
    validate_inputs,
    is_request_too_frequent,
    request_logger,
    is_request_restricted,
)
import time
from django.http import HttpResponse
from datetime import datetime, timedelta


def restrict_request(limit=1000, duration=timedelta(days=1), restrict_super_user=True, resp_msg=None):
    validate_inputs(
        integer=limit, datetimedelta=duration, 
        boolean=restrict_super_user, string=resp_msg
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


def hold_frequent_requests(duration_bw_reqs=timedelta(seconds=1), hold_duration=2):
    validate_inputs(
        datetimedelta=duration_bw_reqs, integer=hold_duration,
    )

    def view_restrict(function):
        def wrapper(request, *args, **kwargs):
            if is_request_too_frequent(request, duration=duration_bw_reqs):
                time.sleep(hold_duration)

            return function(request, *args, **kwargs)
        return wrapper
    return view_restrict


def log_request(function):
    def wrapper(request, *args, **kwargs):
        request_logger(request)

        return function(request, *args, **kwargs)
    wrapper.__doc__ = function.__doc__
    wrapper.__name__ = function.__name__
    return wrapper
