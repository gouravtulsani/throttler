from django.db import models

# Create your models here.


class RequestLogMixin(models.Model):
    user = models.CharField(
        max_length=255,
        null=True,
        db_index=True,
    )
    request_url = models.CharField(
        max_length=255,
        null=True,
        db_index=True,
    )

    class Meta:
        app_label = 'throttle'
        abstract = True


class RequestLog(RequestLogMixin):
    first_attempt = models.DateTimeField()
    req_count = models.PositiveIntegerField()

    class Meta:
        unique_together = ('user', 'request_url')



class RequestLogHistory(RequestLogMixin):
    request_time = models.DateTimeField(
        auto_now_add=True,
    )
    class Meta:
        ordering = ['-request_time']
        app_label = 'throttle'
        index_together = ['user', 'request_url']
