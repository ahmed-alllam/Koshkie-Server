import random
import string

from django.contrib.auth.models import User
from django.db import models


def photo_upload(instance, filename):
    res = instance.id.join(random.choices(string.ascii_letters, k=20))
    return 'accounts/{0}'.format(res)


class UserProfileModel(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    profile_photo = models.ImageField(upload_to=photo_upload)

    def __str__(self):
        return self.user.username
