from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class SmartLockUser(User):
    encode = models.BooleanField(auto_created=False)


class NFTKey(models.Model):
    identifier = models.CharField(max_length=255, null=True, blank=True)
    contract = models.CharField(max_length=255, null=True, blank=True)
    image_url = models.CharField(max_length=255, null=True, blank=True)
    user = models.ForeignKey(User, related_name="nfts", on_delete=models.CASCADE)
