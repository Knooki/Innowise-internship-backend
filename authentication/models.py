from django.db import models


class UserToken(models.Model):

    user_id = models.IntegerField(null=False)
    refresh_token = models.CharField(null=False, max_length=1000)
    is_valid = models.BooleanField(default=True, null=False)

    expires_at = models.DateTimeField()
    created_at = models.DateTimeField()
