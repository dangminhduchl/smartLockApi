from django.contrib.auth.models import User
from django.db import models


class Status(models.Model):
    lock = models.BooleanField()
    door = models.BooleanField()
    update_at = models.DateTimeField(auto_now_add=True)


class Request(models.Model):
    user = models.ForeignKey(User, related_name="user", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=True)
    request = models.ForeignKey(Status, related_name="request_status", on_delete=models.CASCADE)
    action = models.ForeignKey(Status, related_name="action_status", on_delete=models.CASCADE)
