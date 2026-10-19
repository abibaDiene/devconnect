from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from community.models import Question, Answer, Project, Application
User=get_user_model()
class PermissionTests(TestCase):
    def setUp(self):
        self.a=User.objects.create_user(username='alice',email='alice@example.com',password='test-pass-1234')
        self.b=User.objects.create_user(username='bob',email='bob@example.com',password='test-pass-1234')
        self.client_a=APIClient();self.client_a.force_authenticate(user=self.a)
        self.client_b=APIClient();self.client_b.force_authenticate(user=self.b)
    def test_cannot_edit_other_post(self):
        post=self.client_a.post('/api/posts/',{'content':'Bonjour'},format='json').data
        response=self.client_b.patch(f"/api/posts/{post['id']}/",{'content':'Modifié'},format='json')
        self.assertEqual(response.status_code,403)
    def test_cannot_accept_answer_from_other_question(self):
        q1=Question.objects.create(author=self.a,title='A',body='Test')
        q2=Question.objects.create(author=self.a,title='B',body='Test')
        answer=Answer.objects.create(author=self.b,question=q2,body='Réponse')
        response=self.client_a.post(f'/api/questions/{q1.id}/accept_answer/',{'answer_id':answer.id},format='json')
        self.assertEqual(response.status_code,400)
    def test_owner_cannot_apply_to_own_project(self):
        p=Project.objects.create(owner=self.a,name='Site web',description='Demo',seeking_collaborators=True)
        response=self.client_a.post('/api/applications/',{'project':p.id,'message':'Salut'},format='json')
        self.assertEqual(response.status_code,400)
    def test_owner_can_accept_application(self):
        p=Project.objects.create(owner=self.a,name='Site web',description='Demo',seeking_collaborators=True)
        response=self.client_b.post('/api/applications/',{'project':p.id,'message':'Je participe'},format='json')
        self.assertEqual(response.status_code,201)
        result=self.client_a.post(f"/api/applications/{response.data['id']}/decide/",{'status':'accepted'},format='json')
        self.assertEqual(result.status_code,200)
        self.assertEqual(result.data['status'],'accepted')


class SearchFilterTests(TestCase):
    def setUp(self):
        self.alice=User.objects.create_user(username='alice',email='alice@demo.test',password='test-pass-1234',skills=['Python','Django'],bio='Backend')
        self.bob=User.objects.create_user(username='bob',email='bob@demo.test',password='test-pass-1234',skills=['React'])
        Question.objects.create(author=self.alice,title='API Django',body='Question backend',tags=['django'])
        Question.objects.create(author=self.bob,title='React',body='Question frontend',tags=['react'])
        Project.objects.create(owner=self.alice,name='API service',description='Backend API',technologies=['Django'],seeking_collaborators=True)
        Project.objects.create(owner=self.bob,name='Site web',description='Frontend',technologies=['React'],seeking_collaborators=False)
    def values(self,url):
        response=self.client.get(url)
        self.assertEqual(response.status_code,200)
        return response.data['results']
    def test_search_users_by_skill(self):
        results=self.values('/api/users/?skill=Python')
        self.assertEqual([x['username'] for x in results],['alice'])
    def test_search_questions_by_tag_and_status(self):
        results=self.values('/api/questions/?tag=django&status=unresolved')
        self.assertEqual([x['title'] for x in results],['API Django'])
        self.assertEqual(self.values('/api/questions/?status=resolved'),[])
    def test_search_projects_by_technology_and_collaboration(self):
        results=self.values('/api/projects/?technology=Django&collaboration=open')
        self.assertEqual([x['name'] for x in results],['API service'])
        self.assertEqual(self.values('/api/projects/?technology=Django&collaboration=closed'),[])
    def test_no_results_for_unknown_keyword(self):
        self.assertEqual(self.values('/api/posts/?search=introuvable'),[])
