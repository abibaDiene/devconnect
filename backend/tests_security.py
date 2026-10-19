from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from rest_framework.test import APIClient
from community.models import Post, Question, Answer, Report, Project

User = get_user_model()

class SecurityTests(TestCase):
    def setUp(self):
        self.a = User.objects.create_user(username='author9', email='author9@example.test', password='SafePass123!')
        self.b = User.objects.create_user(username='reader9', email='reader9@example.test', password='SafePass123!')
        self.admin = User.objects.create_superuser(username='admin9', email='admin9@example.test', password='SafePass123!')
        self.post = Post.objects.create(author=self.a, content='Texte de test')
        self.question = Question.objects.create(author=self.a, title='Question test', body='Corps')

    def test_unauthenticated_cannot_create_post(self):
        self.assertIn(self.client.post('/api/posts/', {'content':'Bonjour'}).status_code, (401,403))

    def test_another_user_cannot_edit_post(self):
        c=APIClient();c.force_authenticate(user=self.b)
        self.assertEqual(c.patch(f'/api/posts/{self.post.id}/',{'content':'Attaque'},format='json').status_code,403)

    def test_regular_user_cannot_resolve_report(self):
        report=Report.objects.create(reporter=self.b, post=self.post, reason='Texte à revoir')
        c=APIClient();c.force_authenticate(user=self.b)
        self.assertEqual(c.post(f'/api/reports/{report.id}/resolve/',{'decision':'hide'},format='json').status_code,403)

    def test_hidden_question_cannot_receive_answer(self):
        self.question.is_hidden=True;self.question.save(update_fields=['is_hidden'])
        c=APIClient();c.force_authenticate(user=self.b)
        self.assertEqual(c.post('/api/answers/',{'question':self.question.id,'body':'Réponse'},format='json').status_code,400)

    def test_hidden_post_cannot_receive_comment(self):
        self.post.is_hidden=True;self.post.save(update_fields=['is_hidden'])
        c=APIClient();c.force_authenticate(user=self.b)
        self.assertEqual(c.post(f'/api/posts/{self.post.id}/comments/',{'content':'Salut'},format='json').status_code,404)

    def test_regular_user_cannot_suspend_another(self):
        c=APIClient();c.force_authenticate(user=self.a)
        self.assertEqual(c.post(f'/api/users/{self.b.id}/set_active/',{'is_active':False},format='json').status_code,403)

    def test_csrf_required_for_login(self):
        c=APIClient(enforce_csrf_checks=True)
        response=c.post('/api/auth/login/',{'username':'author9','password':'SafePass123!'},format='json')
        self.assertEqual(response.status_code,403)

    def test_login_with_csrf_token(self):
        c=APIClient(enforce_csrf_checks=True)
        c.get('/api/auth/csrf/')
        token=c.cookies['csrftoken'].value
        response=c.post('/api/auth/login/',{'username':'author9','password':'SafePass123!'},format='json',HTTP_X_CSRFTOKEN=token)
        self.assertEqual(response.status_code,200)

    def test_non_admin_cannot_view_other_reports(self):
        Report.objects.create(reporter=self.a,post=self.post,reason='Une raison assez longue')
        c=APIClient();c.force_authenticate(user=self.b)
        response=c.get('/api/reports/')
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.data['count'],0)
