import pytest
from django.urls import reverse

@pytest.mark.django_db
def test_dashboard_redirect_unauthenticated(client):
    url = reverse('core:dashboard')
    response = client.get(url)
    assert response.status_code == 302
    assert '/accounts/login/' in response.url

@pytest.mark.django_db
def test_mission_admin_dashboard(client, mission_admin):
    client.force_login(mission_admin)
    url = reverse('core:dashboard')
    response = client.get(url)
    assert response.status_code == 200
    assert 'mission_dashboard.html' in [t.name for t in response.templates]

@pytest.mark.django_db
def test_member_dashboard(client, member):
    client.force_login(member)
    url = reverse('core:dashboard')
    response = client.get(url)
    assert response.status_code == 200
    assert 'member_dashboard.html' in [t.name for t in response.templates]
