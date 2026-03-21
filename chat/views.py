from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.safestring import mark_safe
import json
from .models import Message


@login_required
def home(request):
    rooms = list(
        Message.objects.values_list('room_name', flat=True).distinct()
    )
    return render(request, 'home.html', {
        'rooms': rooms,
    })


@login_required
def room(request, room_name):
    msgs = Message.objects.filter(room_name=room_name).order_by('-id')[:50][::-1]
    return render(request, 'chat/room.html', {
        'room_name_json': mark_safe(json.dumps(room_name)),
        'room_name': room_name,
        'username': request.user.username,
        'msgs': msgs
    })
    