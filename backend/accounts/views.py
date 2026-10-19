from django.contrib.auth import authenticate, login, logout, get_user_model
from django.db.models import Q
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from rest_framework.throttling import SimpleRateThrottle
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes, action, throttle_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from .serializers import RegisterSerializer, MeSerializer, UserSerializer
User=get_user_model()
class AuthRateThrottle(SimpleRateThrottle):
    scope = 'login'
    def get_cache_key(self, request, view):
        return self.get_ident(request)
class RegistrationRateThrottle(AuthRateThrottle):
    scope = 'register'

@api_view(['GET'])
@permission_classes([AllowAny])
@ensure_csrf_cookie
def csrf_view(request): return Response({'detail':'CSRF cookie initialized'})
@csrf_protect
@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([RegistrationRateThrottle])
def register(request):
    serializer=RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user=serializer.save()
    return Response(MeSerializer(user).data,status=status.HTTP_201_CREATED)
@csrf_protect
@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([AuthRateThrottle])
def login_view(request):
    user=authenticate(request,username=request.data.get('username'),password=request.data.get('password'))
    if user is None or not user.is_active:
        return Response({'detail':'Identifiants invalides'},status=status.HTTP_400_BAD_REQUEST)
    login(request,user)
    return Response(MeSerializer(user).data)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    logout(request)
    return Response(status=status.HTTP_204_NO_CONTENT)
@api_view(['GET','PATCH'])
@permission_classes([IsAuthenticated])
def me(request):
    if request.method=='GET': return Response(MeSerializer(request.user).data)
    serializer=MeSerializer(request.user,data=request.data,partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)
class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset=User.objects.filter(is_active=True).order_by('id')
    serializer_class=UserSerializer
    permission_classes=[AllowAny]
    def get_queryset(self):
        qs=User.objects.all().order_by('id') if self.action == 'set_active' and self.request.user.is_staff else super().get_queryset()
        search=self.request.query_params.get('search','').strip()[:120]
        skill=self.request.query_params.get('skill','').strip()[:60]
        if search: qs=qs.filter(Q(username__icontains=search)|Q(bio__icontains=search)|Q(location__icontains=search))
        if skill: qs=qs.filter(skills__contains=[skill])
        return qs.order_by('-id' if self.request.query_params.get('ordering')=='newest' else 'username','id')

    @action(detail=True,methods=['post'],permission_classes=[IsAdminUser])
    def set_active(self,request,pk=None):
        user=self.get_object()
        if type(request.data.get('is_active')) is not bool:
            return Response({'detail':'is_active doit être un booléen.'},status=400)
        desired=request.data['is_active']
        if user.pk==request.user.pk and not desired:
            return Response({'detail':'Vous ne pouvez pas suspendre votre propre compte.'},status=400)
        if user.is_superuser and not desired:
            return Response({'detail':'Impossible de suspendre un superutilisateur.'},status=403)
        user.is_active=desired
        user.save(update_fields=['is_active'])
        return Response({'id':user.pk,'is_active':user.is_active})
