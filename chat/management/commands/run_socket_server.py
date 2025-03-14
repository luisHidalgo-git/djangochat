from django.core.management.base import BaseCommand
from chat.socket_server import run_socket_server

class Command(BaseCommand):
    help = 'Runs the Socket.IO server'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting Socket.IO server...'))
        run_socket_server()