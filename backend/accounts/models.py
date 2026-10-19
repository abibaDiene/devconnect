from django.contrib.auth.models import AbstractUser
from django.db import models
class User(AbstractUser):
    email = models.EmailField(unique=True)
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=120,blank=True)
    skills = models.JSONField(default=list,blank=True)
    github_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    portfolio_url = models.URLField(blank=True)
    REQUIRED_FIELDS = ['email']
    def __str__(self): return self.username
