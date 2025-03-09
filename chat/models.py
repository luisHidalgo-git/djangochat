from django.db import models
from django.conf import settings

class Message(models.Model):
    SENT = 'sent'  # Una palomita gris
    DELIVERED = 'delivered'  # Dos palomitas grises
    READ = 'read'  # Dos palomitas azules
    
    STATUS_CHOICES = [
        (SENT, 'Sent'),
        (DELIVERED, 'Delivered'),
        (READ, 'Read'),
    ]
    
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=SENT)