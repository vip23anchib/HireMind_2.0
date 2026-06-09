'''
from django.core.management.base import BaseCommand

from faker import Faker

from relationships.models import Author

from applicants.models import UserData

fake = Faker()


class Command(BaseCommand):

    def add_arguments(self, parser):

        parser.add_argument(
            'total',
            type=int
        )

    def handle(self, *args, **kwargs):

        total = kwargs['total']

        authors = []

        for _ in range(total):

            authors.append(
                Author(
                    name=fake.name()
                )
            )

        Author.objects.bulk_create(authors)

        self.stdout.write(
            self.style.SUCCESS(
                f'{total} authors created'
            )
        )
    


for _ in range(1000):

    UserData.objects.create(
        name=fake.name(),
        email=fake.unique.email(),
        gender='Male',
        country='India',
        message='Test'
    )
'''

from django.core.management.base import BaseCommand
from faker import Faker

from applicants.models import UserData

fake = Faker()


class Command(BaseCommand):

    def add_arguments(self, parser):

        parser.add_argument(
            'total',
            type=int
        )

    def handle(self, *args, **kwargs):

        total = kwargs['total']

        candidates = []

        for _ in range(total):

            candidates.append(
                UserData(
                    name=fake.name(),
                    email=fake.unique.email(),
                    gender='Male',
                    country='India',
                    phone_number='9999999999',
                    cover_letter='Test Cover Letter',
                    linkedin_url='https://linkedin.com',
                    portfolio_url='https://github.com'
                )
            )

        UserData.objects.bulk_create(candidates)

        self.stdout.write(
            self.style.SUCCESS(
                f'{total} candidates created'
            )
        )