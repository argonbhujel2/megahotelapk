"""Critical path tests — authentication and order creation rules."""
import pytest
from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.delivery import DeliveryIdentitySlot
from werkzeug.security import generate_password_hash


@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "ADMIN_BOOTSTRAP_ENABLED": False,
        "JWT_SECRET_KEY": "test-secret",
    })
    with app.app_context():
        db.create_all()
        # Seed two delivery slots
        db.session.add(DeliveryIdentitySlot(id=1))
        db.session.add(DeliveryIdentitySlot(id=2))
        db.session.commit()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def test_health(client):
    rv = client.get("/health")
    assert rv.status_code == 200
    assert rv.get_json()["status"] == "ok"


def test_login_invalid(client):
    rv = client.post("/api/v1/auth/login", json={"email": "x@y.com", "password": "wrong"})
    assert rv.status_code == 401


def test_guest_entry(client):
    rv = client.post("/api/v1/auth/guest")
    assert rv.status_code == 200
    assert rv.get_json()["guest"] is True


def test_only_two_delivery_slots(client, app):
    with app.app_context():
        slots = DeliveryIdentitySlot.query.all()
        assert len(slots) == 2
        assert {s.id for s in slots} == {1, 2}


def test_create_order_requires_payment_method(client):
    rv = client.post("/api/v1/orders", json={
        "items": [],
        "payment_method": "esewa",  # not allowed
        "is_guest": True,
        "guest_name": "Test",
        "guest_phone": "9800000000",
        "address": {"full_address": "Kathmandu"},
    })
    assert rv.status_code == 400
    assert "COD or QR" in rv.get_json()["message"]
