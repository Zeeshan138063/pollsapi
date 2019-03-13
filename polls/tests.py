from django.test import TestCase
from rest_framework.test import APITestCase

# Create your tests here.
from rest_framework.test import APIRequestFactory
from polls.views import *

class TestPoll(APITestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = PollViewSet.as_view({'get':'list'})
        self.uri = '/polls/'

    def test_list(self):
        request = self.factory.get(self.uri)
        response = self.view(request)
        self.assertEqual(response.status_code,2000,
                         'Expected Response Code 200, received {0}'
                         ' instead.'.format(response.status_code)
                         )


