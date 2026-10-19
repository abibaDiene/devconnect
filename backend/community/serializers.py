from rest_framework import serializers
from .models import Post,Comment,Reaction,Question,Answer,Project,Application,Report
class PostSerializer(serializers.ModelSerializer):
    comments_count=serializers.IntegerField(source='comments.count',read_only=True)
    reactions_count=serializers.IntegerField(source='reactions.count',read_only=True)
    class Meta:
        model=Post
        fields=['id','author','content','created_at','updated_at','comments_count','reactions_count']
        read_only_fields=['id','author','created_at','updated_at']
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model=Comment
        fields=['id','author','post','content','created_at']
        read_only_fields=['id','author','post','created_at']
class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model=Question
        fields=['id','author','title','body','tags','accepted_answer','created_at']
        read_only_fields=['id','author','accepted_answer','created_at']
class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model=Answer
        fields=['id','author','question','body','created_at']
        read_only_fields=['id','author','created_at']
class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model=Project
        fields=['id','owner','name','description','technologies','github_url','demo_url','seeking_collaborators','created_at']
        read_only_fields=['id','owner','created_at']
class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model=Application
        fields=['id','project','applicant','message','status','created_at']
        read_only_fields=['id','applicant','status','created_at']
class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model=Report
        fields=['id','reporter','post','question','reason','resolved','created_at']
        read_only_fields=['id','reporter','resolved','created_at']
    def validate(self,attrs):
        if bool(attrs.get('post')) == bool(attrs.get('question')):
            raise serializers.ValidationError('Signalez une publication OU une question.')
        return attrs
