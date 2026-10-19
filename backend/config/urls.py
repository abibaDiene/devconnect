from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from community.views import PostViewSet, QuestionViewSet, AnswerViewSet, ProjectViewSet, ApplicationViewSet, ReportViewSet
from accounts.views import register, login_view, logout_view, csrf_view, me, UserViewSet
router = DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register('posts', PostViewSet, basename='posts')
router.register('questions', QuestionViewSet, basename='questions')
router.register('answers', AnswerViewSet, basename='answers')
router.register('projects', ProjectViewSet, basename='projects')
router.register('applications', ApplicationViewSet, basename='applications')
router.register('reports', ReportViewSet, basename='reports')
urlpatterns = [path('admin/',admin.site.urls),path('api/auth/register/',register),
    path('api/auth/login/',login_view),path('api/auth/logout/',logout_view),
    path('api/auth/csrf/',csrf_view),path('api/auth/me/',me),path('api/',include(router.urls))]
