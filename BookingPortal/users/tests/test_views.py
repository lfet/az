from django.test import TestCase, Client, SimpleTestCase
from django.contrib.auth.models import User


class CreateUserTest(TestCase):

    # def setUp(self):
    #     self.client = Client()


    def test_user_created(self):
        client = Client()
        username = 'testUser1'
        password = 'unsafe123'

        response = client.post('/register', {
            'username': 'testUser1',
            'password': 'unsafe123',
            'userType': 'User'
        })

        self.asserEtquals(response.status_code, 301)
        newUser = User.objects.all().last()
        self.assertEquals(newUser.username, 'testUser1')



