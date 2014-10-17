from django.db import models
from django.utils import timezone

from myauth.models import MyUser
from core.models import Community

class ShoppingListEntry(models.Model):
    community = models.ForeignKey(Community)
    user = models.ForeignKey(MyUser)
    subject = models.CharField(max_length=32)
    description = models.CharField(max_length=1024, blank=True)
    time_created = models.DateTimeField(default=timezone.now)
    time_done = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.subject

class ChatEntry(models.Model):
    community = models.ForeignKey(Community)
    user = models.ForeignKey(MyUser)
    message = models.CharField(max_length=1024)

    def __str__(self):
        return str(self.user) + ": " + self.message
