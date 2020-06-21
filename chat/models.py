from django.contrib.auth.models import User
from django.db import models

# Create your models here.

class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=100)
    message = models.CharField(max_length=5000)
    date_sent = models.DateTimeField(auto_now_add=True, blank=True)
    room_name = models.CharField(max_length=100)
    room_group_name = models.CharField(max_length=100)

    