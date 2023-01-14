from unittest.mock import Mock, patch

from django.urls import reverse
from rest_framework.test import APIClient, APITestCase

from src.users.models import User


class TestTeamAPI(APITestCase):
    def setUp(self):
        self.client = APIClient()

        self.teams_url = reverse("api:futsal_sim:teams-list")

    @patch("src.futsal_sim.apis.teams_api.TeamCRUDService.team_create")
    def test_create_logged_in(self, team_create_mock: Mock):
        data = {"name": "nico"}

        user = User.objects.create_user(email="testuser@123.com", password="123456")
        self.client.force_login(user)

        response = self.client.post(self.teams_url, data)
        self.assertEqual(201, response.status_code)

        team_create_mock.assert_called()

    @patch("src.futsal_sim.apis.teams_api.TeamCRUDService.team_create")
    def test_create_not_logged_in(self, team_create_mock: Mock):
        data = {"name": "nico"}

        response = self.client.post(self.teams_url, data)
        self.assertEqual(403, response.status_code)

        team_create_mock.assert_not_called()
