from app.models.user import User, Role
from app.models.organization import Organization


def test_user_model_exists():
    user = User(username="test", hashed_password="x", role=Role.DATA_HOLDER)
    assert user.username == "test"
    assert user.role == Role.DATA_HOLDER


def test_organization_model_exists():
    org = Organization(name="测试机构", org_type="enterprise")
    assert org.name == "测试机构"


def test_all_roles_defined():
    expected = {"data_holder", "registry_center", "assessor", "compliance", "regulator", "admin"}
    actual = {r.value for r in Role}
    assert actual == expected
