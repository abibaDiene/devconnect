from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
User = get_user_model()
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=['id','username','bio','location','skills','github_url','linkedin_url','portfolio_url','date_joined']
        read_only_fields=['id','date_joined']
class MeSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        fields=UserSerializer.Meta.fields+['email','is_staff']
class RegisterSerializer(serializers.ModelSerializer):
    password=serializers.CharField(write_only=True,validators=[validate_password])
    class Meta:
        model=User
        fields=['id','username','email','password']
        read_only_fields=['id']
    def create(self,validated_data):
        return User.objects.create_user(**validated_data)
