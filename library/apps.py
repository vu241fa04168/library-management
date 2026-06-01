from django.apps import AppConfig
from django.db.models.signals import post_migrate

def create_publisher_group(sender, **kwargs):
    from django.contrib.auth.models import Group
    Group.objects.get_or_create(name='Publisher')

class LibraryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'library'

    def ready(self):
        post_migrate.connect(create_publisher_group, sender=self)
