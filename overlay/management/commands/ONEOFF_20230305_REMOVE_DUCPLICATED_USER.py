import time
from django.core.management.base import BaseCommand
from overlay.models import User


class Command(BaseCommand):
    """
        Remove duplicated user
    """

    def run_command(self):
        for family in User.objects.values_list('family', flat=True).distinct():
            User.objects.filter(pk__in=User.objects.filter(family=family).values_list('id', flat=True)[1:]).delete()

    def handle(self, *args, **options):
        begin = time.time()

        self.stdout.write(self.style.SUCCESS('Running...'))

        self.run_command()

        self.stdout.write(self.style.SUCCESS('Success! :)'))
        self.stdout.write(self.style.SUCCESS(
            f'Done with {time.time() - begin}s'))
