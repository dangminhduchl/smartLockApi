from django.db import models

class Status(models.Model):
    lock = models.BooleanField()
    door = models.BooleanField()
    update_at = models.DateTimeField(auto_now_add=True)
