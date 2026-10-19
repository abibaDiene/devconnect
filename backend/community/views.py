from django.db.models import Q
from rest_framework import viewsets,status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated,IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from .models import Post,Comment,Reaction,Question,Answer,Project,Application,Report
from .serializers import PostSerializer,CommentSerializer,QuestionSerializer,AnswerSerializer,ProjectSerializer,ApplicationSerializer,ReportSerializer
class OwnerWritePermission(IsAuthenticatedOrReadOnly):
    def has_object_permission(self,request,view,obj):
        if request.method in ('GET','HEAD','OPTIONS'): return True
        owner=getattr(obj,'author',getattr(obj,'owner',None))
        return bool(request.user.is_authenticated and (request.user.is_staff or owner == request.user))
class PostViewSet(viewsets.ModelViewSet):
    queryset=Post.objects.select_related('author').order_by('-created_at')
    serializer_class=PostSerializer
    permission_classes=[OwnerWritePermission]
    def perform_create(self,serializer): serializer.save(author=self.request.user)
    @action(detail=True,methods=['get','post'],permission_classes=[IsAuthenticatedOrReadOnly])
    def comments(self,request,pk=None):
        post=self.get_object()
        if request.method=='GET':
            return Response(CommentSerializer(post.comments.order_by('created_at'),many=True).data)
        serializer=CommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(post=post,author=request.user)
        return Response(serializer.data,status=status.HTTP_201_CREATED)
    @action(detail=True,methods=['post'],permission_classes=[IsAuthenticated])
    def react(self,request,pk=None):
        post=self.get_object()
        reaction,created=Reaction.objects.get_or_create(post=post,author=request.user)
        if not created: reaction.delete()
        return Response({'reacted':created})
class QuestionViewSet(viewsets.ModelViewSet):
    queryset=Question.objects.select_related('author','accepted_answer').order_by('-created_at')
    serializer_class=QuestionSerializer
    permission_classes=[OwnerWritePermission]
    def perform_create(self,serializer): serializer.save(author=self.request.user)
    @action(detail=True,methods=['post'],permission_classes=[IsAuthenticated])
    def accept_answer(self,request,pk=None):
        question=self.get_object()
        if question.author_id != request.user.id: return Response({'detail':'Action interdite'},status=403)
        answer=question.answers.filter(pk=request.data.get('answer_id')).first()
        if answer is None: return Response({'detail':'Réponse introuvable pour cette question'},status=400)
        question.accepted_answer=answer;question.save(update_fields=['accepted_answer'])
        return Response(QuestionSerializer(question).data)
class AnswerViewSet(viewsets.ModelViewSet):
    queryset=Answer.objects.select_related('author','question').order_by('created_at')
    serializer_class=AnswerSerializer
    permission_classes=[OwnerWritePermission]
    def perform_create(self,serializer): serializer.save(author=self.request.user)
    def get_queryset(self):
        qs=super().get_queryset()
        question_id=self.request.query_params.get('question')
        if question_id: qs=qs.filter(question_id=question_id)
        return qs
class ProjectViewSet(viewsets.ModelViewSet):
    queryset=Project.objects.select_related('owner').order_by('-created_at')
    serializer_class=ProjectSerializer
    permission_classes=[OwnerWritePermission]
    def perform_create(self,serializer): serializer.save(owner=self.request.user)
    def get_queryset(self):
        qs=super().get_queryset()
        search=self.request.query_params.get('search','').strip()
        if search: qs=qs.filter(Q(name__icontains=search)|Q(description__icontains=search))
        return qs
class ApplicationViewSet(viewsets.ModelViewSet):
    serializer_class=ApplicationSerializer
    http_method_names=['get','post','head','options']
    permission_classes=[IsAuthenticated]
    def get_queryset(self):
        return Application.objects.filter(Q(applicant=self.request.user)|Q(project__owner=self.request.user)).select_related('project','applicant').order_by('-created_at')
    def perform_create(self,serializer):
        from rest_framework.exceptions import ValidationError
        project=serializer.validated_data['project']
        if not project.seeking_collaborators or project.owner_id == self.request.user.pk:
            raise ValidationError('Candidature impossible pour ce projet.')
        if Application.objects.filter(project=project,applicant=self.request.user).exists():
            raise ValidationError('Candidature déjà envoyée.')
        serializer.save(applicant=self.request.user)
    @action(detail=True,methods=['post'])
    def decide(self,request,pk=None):
        application=self.get_object()
        if application.project.owner_id != request.user.id: return Response({'detail':'Action interdite'},status=403)
        decision=request.data.get('status')
        if decision not in ['accepted','rejected'] or application.status != 'pending':
            return Response({'detail':'Décision invalide'},status=400)
        application.status=decision;application.save(update_fields=['status'])
        return Response(self.get_serializer(application).data)
class ReportViewSet(viewsets.ModelViewSet):
    serializer_class=ReportSerializer
    permission_classes=[IsAuthenticated]
    http_method_names=['get','post','head','options']
    def get_queryset(self):
        if self.request.user.is_staff: return Report.objects.all().order_by('-created_at')
        return Report.objects.filter(reporter=self.request.user).order_by('-created_at')
    def perform_create(self,serializer): serializer.save(reporter=self.request.user)
