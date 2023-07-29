import time
from django.core.management.base import BaseCommand
from overlay.models import OverlayType, OverlayReference


class Command(BaseCommand):
    """
        Populate overlayType and overlayReference
    """

    def run_command(self):
        single = OverlayType(
            name='x1_bdo',
            description='Overlay padrao x1 blackdesert',
            default=True
        )
        single.save()

        doubles = OverlayType(
            name='x2_bdo',
            description='Overlay de duplas blackdesert',
            default=False
        )
        doubles.save()

        trio = OverlayType(
            name='x3_bdo',
            description='Overlay de trios blackdesert',
            default=False
        )
        trio.save()

        street_fighter = OverlayType(
            name='street_fighter',
            description='Overlay padrao de street fighter',
            default=False
        )
        street_fighter.save()

        single_ref = OverlayReference(
            overlay=single,
            reference='PREMIUM'
        )
        single_ref.save()

        doubles_ref = OverlayReference(
            overlay=doubles,
            reference='DUPLAS'
        )
        doubles_ref.save()

        trio_ref = OverlayReference(
            overlay=trio,
            reference='TRIOS'
        )
        trio_ref.save()

        street_fighter_ref = OverlayReference(
            overlay=street_fighter,
            reference='STREET FIGHTER'
        )
        street_fighter_ref.save()

    def handle(self, *args, **options):
        begin = time.time()

        self.stdout.write(self.style.SUCCESS('Running...'))

        self.run_command()

        self.stdout.write(self.style.SUCCESS('Success! :)'))
        self.stdout.write(self.style.SUCCESS(
            f'Done with {time.time() - begin}s'))
