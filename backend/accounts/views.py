from django.contrib.auth import authenticate, login, logout, get_user_model
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from .serializers import RegisterSerializer, MeSerializer, UserSerializer
User=get_user_model()
@api_view(['GET'])
@permission_classes([AllowAny])
@ensure_csrf_cookie
def csrf_view(request): return Response({'detail':'CSRF cookie initialized'})
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer=RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user=serializer.save()
    return Response(MeSerializer(user).data,status=status.HTTP_201_CREATED)
@api_view(['POST'])
@permission_classes([AllowAny])
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
        qs=super().get_queryset()
        search=self.request.query_params.get('search','').strip()
        if search: qs=qs.filter(username__icontains=search)
        return qs
