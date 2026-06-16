from django.apps import AppConfig


class UserprofileConfig(AppConfig):
    name = 'profile'
    
    def ready(self):
        import accounts.signals