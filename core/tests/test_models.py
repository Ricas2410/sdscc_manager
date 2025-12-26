import pytest
from core.models import Area, District, Branch

@pytest.mark.django_db
class TestHierarchy:
    def test_area_creation(self):
        area = Area.objects.create(name="Test Area", code="TA")
        assert area.name == "Test Area"
        assert str(area) == "Test Area (TA)"

    def test_district_creation(self, area):
        district = District.objects.create(name="Test District", code="TD", area=area)
        assert district.area == area
        assert str(district) == "Test District (TD) - Test Area"

    def test_branch_creation(self, district):
        branch = Branch.objects.create(
            name="Test Branch", 
            code="TB", 
            district=district,
            monthly_tithe_target=1000
        )
        assert branch.district == district
        assert branch.full_hierarchy == "Test Area > Test District > Test Branch"
