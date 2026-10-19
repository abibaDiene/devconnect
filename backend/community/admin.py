from django.contrib import admin
from .models import Post,Comment,Reaction,Question,Answer,Project,Application,Report
for model in [Post,Comment,Reaction,Question,Answer,Project,Application,Report]:
    admin.site.register(model)
