from django.db import models
from django.contrib.auth import models as user_model
# Create your models here.

class Dataset(models.Model):
    user = models.ForeignKey(user_model.User, on_delete=models.CASCADE())
    location = models.TextField()
    description = models.TextField()
    create_at = models.DateTimeField(auto_now_add=True)
    modifile_at = models.DateTimeField(auto_now=True)

