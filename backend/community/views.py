from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import viewsets,status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated,IsAuthenticatedOrReadOnly,IsAdminUser
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
    def get_queryset(self):
        qs=super().get_queryset()
        if not self.request.user.is_staff:
            qs=qs.filter(is_hidden=False)
        term=self.request.query_params.get('search','').strip()[:120]
        if term: qs=qs.filter(Q(content__icontains=term)|Q(author__username__icontains=term))
        return qs.order_by('created_at' if self.request.query_params.get('ordering')=='oldest' else '-created_at')
    @action(detail=True,methods=['get','post'],permission_classes=[IsAuthenticatedOrReadOnly])
    def comments(self,request,pk=None):
        post=self.get_object()
        if request.method=='GET':
            return Response(CommentSerializer(post.comments.order_by('created_at'),many=True).data)
        if post.is_hidden: return Response({'detail':'Publication indisponible.'},status=404)
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
    def get_queryset(self):
        qs=super().get_queryset()
        if not self.request.user.is_staff: qs=qs.filter(is_hidden=False)
        params=self.request.query_params
        term=params.get('search','').strip()[:120]
        tag=params.get('tag','').strip()[:60]
        if term: qs=qs.filter(Q(title__icontains=term)|Q(body__icontains=term)|Q(author__username__icontains=term))
        if tag: qs=qs.filter(tags__contains=[tag])
        if params.get('status')=='resolved': qs=qs.filter(accepted_answer__isnull=False)
        elif params.get('status')=='unresolved': qs=qs.filter(accepted_answer__isnull=True)
        return qs.order_by('created_at' if params.get('ordering')=='oldest' else '-created_at')
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
    def perform_create(self,serializer):
        from rest_framework.exceptions import ValidationError
        if serializer.validated_data['question'].is_hidden:
            raise ValidationError('Impossible de répondre à une question masquée.')
        serializer.save(author=self.request.user)
    def get_queryset(self):
        qs=super().get_queryset()
        if not self.request.user.is_staff: qs=qs.filter(question__is_hidden=False)
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
        params=self.request.query_params
        search=params.get('search','').strip()[:120]
        tech=params.get('technology','').strip()[:60]
        if search: qs=qs.filter(Q(name__icontains=search)|Q(description__icontains=search)|Q(owner__username__icontains=search))
        if tech: qs=qs.filter(technologies__contains=[tech])
        if params.get('collaboration')=='open': qs=qs.filter(seeking_collaborators=True)
        elif params.get('collaboration')=='closed': qs=qs.filter(seeking_collaborators=False)
        return qs.order_by('created_at' if params.get('ordering')=='oldest' else '-created_at')
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
        if self.request.user.is_staff: return Report.objects.select_related('reporter','post','question').order_by('-created_at')
        return Report.objects.filter(reporter=self.request.user).order_by('-created_at')
    def perform_create(self,serializer): serializer.save(reporter=self.request.user)

    @action(detail=True,methods=['post'],permission_classes=[IsAdminUser])
    def resolve(self,request,pk=None):
        report=self.get_object()
        if report.resolved: return Response({'detail':'Signalement déjà traité.'},status=400)
        decision=request.data.get('decision')
        if decision not in ('hide','dismiss'):
            return Response({'detail':'Décision attendue : hide ou dismiss.'},status=400)
        if decision=='hide':
            target=report.post or report.question
            if target is None: return Response({'detail':'Contenu introuvable.'},status=400)
            target.is_hidden=True
            target.save(update_fields=['is_hidden'])
        report.resolved=True
        report.save(update_fields=['resolved'])
        return Response(self.get_serializer(report).data)
