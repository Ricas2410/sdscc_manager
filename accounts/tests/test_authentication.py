import pytest
from django.urls import reverse
from accounts.models import User

@pytest.mark.django_db
class TestAuthentication:
    def test_login_view(self, client, member):
        url = reverse('accounts:login')
        response = client.get(url)
        assert response.status_code == 200
        
        # Test valid login
        response = client.post(url, {
            'member_id': member.member_id,
            'password': 'password123'
        })
        assert response.status_code == 302
        assert response.url == reverse('core:dashboard')

    def test_invalid_login(self, client):
        url = reverse('accounts:login')
        response = client.post(url, {
            'member_id': 'INVALID',
            'password': 'wrongpassword'
        })
        assert response.status_code == 200
        # View uses manual form handling, so no 'form' in context
        messages = list(response.context['messages'])
        assert any('Invalid Member ID or password' in str(m) for m in messages)

    def test_user_creation(self):
        user = User.objects.create_user(
            member_id='NEW001',
            password='password123',
            first_name='New',
            last_name='User'
        )
        assert user.check_password('password123')
        assert user.role == User.Role.MEMBER
