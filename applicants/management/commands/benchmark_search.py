import time

from django.core.management.base import BaseCommand

from applicants.models import UserSkill


class Command(BaseCommand):

    def handle(self, *args, **kwargs):

        start = time.perf_counter()

        list(
            UserSkill.objects.filter(
                skill__name="Python"
            )
        )

        end = time.perf_counter()

        print(
            f"Execution Time: {end - start:.8f} seconds"
        )