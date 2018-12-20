# Django Throttle

* Throttle is an django app use to throttle Web APIs. <br />
**throttle** is a very simple way to log each and every api requests. <br />
Also can be use to restrict user request <br />
to a certain limit in a fix amount of time. <br />
Or to hold too frequent requests from specific user <br />

## Installation:
- Fetch the latest code
- Add `'throttle',` into your INSTALLED_APPS inside settings.py
- Run `python manage.py makemigrations throttle && python manage.py migrate`


## Usage:
1. `log_request`: It logs each and every incoming input request from the client to track record if incoming requests.
- *Example*:
    ```python
    from throttle.decorators import logrequest
    ...
    @logrequest
    def api_view():
    ...
    ```
2. `restrict_request`: It restrict the user request when the user exceeds max request limit.
We can add a list of `WHITE_LISTED_USERS` and or `BLACK_LISTED_USERS` in settings if we don't want to restrict users or block users we can add the username to the above lists
- *Example*:
    ```python
    from throttle.decorators import restrict_request
    ...
    @restrict_request(limit=100, duration=timedelta(days=30))
    # the above decorator will restrict api call to 100/day per user
    def api_view():
    ...
    ```
3. `hold_frequent_requests`: It will delay the response if someone is requesting too frequently to an API
- *Example*:
    ```python
    from throttle.decorators import hold_frequent_requests
    ...
    @hold_frequent_requests(duration_bw_reqs=timedelta(seconds=1), hold_duration=5)
    """
    The above decorator will hold the request processing for hold duration,
    if the time diff between prev request and current request is less than expected duration_bw_reqs
    """
    def api_view():
    ...
    ```

