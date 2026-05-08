from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from rest_framework.authtoken.models import Token

from core.models import UserProfile


class Command(BaseCommand):
    help = 'Creates missing profiles and tokens for all existing users.'

    def handle(self, *args, **kwargs):
        profiles_created = 0
        tokens_created = 0

        for user in User.objects.all():
            _, profile_created = UserProfile.objects.get_or_create(user=user)
            _, token_created = Token.objects.get_or_create(user=user)
            profiles_created += int(profile_created)
            tokens_created += int(token_created)

        self.stdout.write(
            self.style.SUCCESS(
                f'Synced users: {User.objects.count()}, created profiles: {profiles_created}, created tokens: {tokens_created}'
            )
        )
