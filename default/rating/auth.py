from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import UserManager


class CustomDatastoreUserManager(UserManager):
    pass


class CustomAuthenticationBackend(ModelBackend):
    pass