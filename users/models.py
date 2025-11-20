from django.contrib.auth.models import AbstractUser
from django.db import models
from .manager import CustomUserManager


# Create your models here.
class CustomUser(AbstractUser):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    organisation = models.CharField(max_length=255, blank=True)
    bio = models.CharField(max_length=255, blank=True)
    username = models.CharField(max_length=150, unique=True)
    image = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    last_seen = models.DateTimeField(blank=True, null=True)
    date_joined=models.DateTimeField(auto_now_add=True, db_index=True)
    

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    objects = CustomUserManager()


    def __str__(self):
        return self.email

