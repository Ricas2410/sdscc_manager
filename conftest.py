import pytest
from accounts.models import User
from core.models import Area, District, Branch

@pytest.fixture
def mission_admin(db):
    user = User.objects.create_user(
        member_id='ADMIN001',
        password='password123',
        first_name='Mission',
        last_name='Admin',
        role=User.Role.MISSION_ADMIN
    )
    return user

@pytest.fixture
def area(db):
    return Area.objects.create(name='Test Area', code='TA')

@pytest.fixture
def district(db, area):
    return District.objects.create(name='Test District', code='TD', area=area)

@pytest.fixture
def branch(db, district):
    return Branch.objects.create(
        name='Test Branch',
        code='TB',
        district=district,
        monthly_tithe_target=1000
    )

@pytest.fixture
def member(db, branch):
    user = User.objects.create_user(
        member_id='MEM001',
        password='password123',
        first_name='John',
        last_name='Doe',
        role=User.Role.MEMBER,
        branch=branch
    )
    return user
