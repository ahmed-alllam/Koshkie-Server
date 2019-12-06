import string

from django.db import models
from django.contrib.auth.models import User
import random


def profile_photo_upload(instance, filename):
    res = ''.join(random.choices(string.ascii_letters, k=30))
    return 'accounts/{0}'.format(res)


class UserProfileModel(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="Profile")
    profile_photo = models.ImageField(upload_to=profile_photo_upload)
