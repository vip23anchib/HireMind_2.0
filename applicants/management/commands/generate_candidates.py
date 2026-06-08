from django.core.management.base import BaseCommand

from faker import Faker

import random

from applicants.models import (
    UserData,
    Skill,
    UserSkill
)

fake = Faker()


class Command(BaseCommand):

    def add_arguments(self, parser):

        parser.add_argument(
            "count",
            type=int
        )

    def handle(self, *args, **kwargs):

        count = kwargs["count"]

        skills = list(
            Skill.objects.all()
        )

        if not skills:

            self.stdout.write(
                self.style.ERROR(
                    "No skills found in Skill table."
                )
            )
            return

        for _ in range(count):

            candidate = UserData.objects.create(

                name=fake.name(),

                email=fake.unique.email(),

                gender=random.choice(
                    ["Male", "Female"]
                ),

                phone_number=fake.msisdn()[:10],

                country=fake.country(),

                cover_letter=fake.text(
                    max_nb_chars=200
                ),

                linkedin_url=f"https://linkedin.com/in/{fake.user_name()}",

                portfolio_url=f"https://github.com/{fake.user_name()}"
            )

            selected_skills = random.sample(
                skills,
                k=min(
                    3,
                    len(skills)
                )
            )

            for skill in selected_skills:

                UserSkill.objects.create(

                    user_data=candidate,

                    skill=skill,

                    years_of_experience=random.randint(
                        1,
                        10
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"{count} fake candidates created successfully."
            )
        )