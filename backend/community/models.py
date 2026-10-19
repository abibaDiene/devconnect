from django.conf import settings
from django.db import models
User=settings.AUTH_USER_MODEL
class TimeStamped(models.Model):
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    class Meta: abstract=True
class Post(TimeStamped):
    author=models.ForeignKey(User,on_delete=models.CASCADE,related_name='posts')
    content=models.TextField()
class Comment(TimeStamped):
    author=models.ForeignKey(User,on_delete=models.CASCADE)
    post=models.ForeignKey(Post,on_delete=models.CASCADE,related_name='comments')
    content=models.TextField()
class Reaction(models.Model):
    author=models.ForeignKey(User,on_delete=models.CASCADE)
    post=models.ForeignKey(Post,on_delete=models.CASCADE,related_name='reactions')
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta: constraints=[models.UniqueConstraint(fields=['author','post'],name='unique_reaction_per_post')]
class Question(TimeStamped):
    author=models.ForeignKey(User,on_delete=models.CASCADE)
    title=models.CharField(max_length=200)
    body=models.TextField()
    tags=models.JSONField(default=list,blank=True)
    accepted_answer=models.ForeignKey('Answer',null=True,blank=True,on_delete=models.SET_NULL,related_name='+')
class Answer(TimeStamped):
    author=models.ForeignKey(User,on_delete=models.CASCADE)
    question=models.ForeignKey(Question,on_delete=models.CASCADE,related_name='answers')
    body=models.TextField()
class Project(TimeStamped):
    owner=models.ForeignKey(User,on_delete=models.CASCADE)
    name=models.CharField(max_length=150)
    description=models.TextField()
    technologies=models.JSONField(default=list,blank=True)
    github_url=models.URLField(blank=True)
    demo_url=models.URLField(blank=True)
    seeking_collaborators=models.BooleanField(default=False)
class Application(TimeStamped):
    class Status(models.TextChoices):
        PENDING='pending','En attente'
        ACCEPTED='accepted','Acceptée'
        REJECTED='rejected','Refusée'
    project=models.ForeignKey(Project,on_delete=models.CASCADE,related_name='applications')
    applicant=models.ForeignKey(User,on_delete=models.CASCADE)
    message=models.TextField()
    status=models.CharField(max_length=12,choices=Status.choices,default=Status.PENDING)
    class Meta: constraints=[models.UniqueConstraint(fields=['project','applicant'],name='unique_project_application')]
class Report(TimeStamped):
    reporter=models.ForeignKey(User,on_delete=models.CASCADE)
    post=models.ForeignKey(Post,null=True,blank=True,on_delete=models.CASCADE)
    question=models.ForeignKey(Question,null=True,blank=True,on_delete=models.CASCADE)
    reason=models.TextField()
    resolved=models.BooleanField(default=False)
