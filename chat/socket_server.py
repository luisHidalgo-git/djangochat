import socketio
import eventlet
from django.contrib.auth.models import User
from .models import Message
from django.core.cache import cache
from django.utils import timezone

sio = socketio.Server(cors_allowed_origins='*')
app = socketio.WSGIApp(sio)

@sio.event
def connect(sid, environ):
    print('Client connected:', sid)

@sio.event
def disconnect(sid):
    print('Client disconnected:', sid)

@sio.event
def join_room(sid, data):
    room_name = data.get('room_name')
    username = data.get('username')
    sio.enter_room(sid, room_name)
    cache.set(f'user_status_{username}', 'online', timeout=None)
    sio.emit('user_status', {'user': username, 'status': 'online'}, room=room_name)

@sio.event
def leave_room(sid, data):
    room_name = data.get('room_name')
    username = data.get('username')
    sio.leave_room(sid, room_name)
    cache.set(f'user_status_{username}', 'offline', timeout=None)
    sio.emit('user_status', {'user': username, 'status': 'offline'}, room=room_name)

@sio.event
def send_message(sid, data):
    room_name = data.get('room_name')
    message_content = data.get('message')
    sender_username = data.get('sender')
    message_type = data.get('message_type', 'normal')
    subject = data.get('subject', 'none')

    try:
        sender = User.objects.get(username=sender_username)
        receiver = User.objects.get(username=room_name)

        message = Message.objects.create(
            sender=sender,
            receiver=receiver,
            content=message_content,
            status=Message.SENT,
            message_type=message_type,
            subject=subject
        )

        sio.emit('new_message', {
            'sender': sender_username,
            'message': message_content,
            'timestamp': message.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            'status': 'sent',
            'message_type': message_type,
            'subject': subject,
            'message_id': str(message.id)
        }, room=room_name)

    except User.DoesNotExist:
        print(f"Error: User not found")
    except Exception as e:
        print(f"Error sending message: {str(e)}")

@sio.event
def update_message(sid, data):
    message_id = data.get('message_id')
    message_type = data.get('message_type')
    subject = data.get('subject')

    try:
        message = Message.objects.get(id=message_id)
        if message_type:
            message.message_type = message_type
        if subject:
            message.subject = subject
        message.save()

        room_name = message.receiver.username
        sio.emit('message_updated', {
            'message_id': message_id,
            'message_type': message_type,
            'subject': subject
        }, room=room_name)

    except Message.DoesNotExist:
        print(f"Error: Message not found")
    except Exception as e:
        print(f"Error updating message: {str(e)}")

def run_socket_server():
    eventlet.wsgi.server(eventlet.listen(('', 5000)), app)