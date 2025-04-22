import pytest
from app import app, db
from models import SwiftCode

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.drop_all()


def test_get_swift_code(client):
    code = SwiftCode(
        address="123 Main St",
        bank_name="Test Bank",
        country_iso2="US",
        country_name="United States",
        is_headquarter=True,
        swift_code="TESTUS33XXX"
    )
    db.session.add(code)
    db.session.commit()

    response = client.get('/v1/swift-codes/TESTUS33XXX')
    assert response.status_code == 200
    assert 'Test Bank' in response.json['bankName']

def test_add_swift_code(client):
    response = client.post('/v1/swift-codes', json={
        "address": "456 Elm St",
        "bankName": "Another Bank",
        "countryISO2": "GB",
        "countryName": "United Kingdom",
        "isHeadquarter": True,
        "swiftCode": "ANOTHGBBXXX"
    })
    assert response.status_code == 201
    assert response.json['message'] == 'SWIFT code added successfully'

def test_get_swift_code_country(client):
    code = SwiftCode(
        address="123 Main St",
        bank_name="Test Bank",
        country_iso2="US",
        country_name="United States",
        is_headquarter=True,
        swift_code="TESTUS33XXX"
    )
    db.session.add(code)
    db.session.commit()
    code = SwiftCode(
        address="223 Main St",
        bank_name="Test Bank2",
        country_iso2="US",
        country_name="United States",
        is_headquarter=False,
        swift_code="TESTUS33123"
    )
    db.session.add(code)
    db.session.commit()

    response = client.get('/v1/swift-codes/country/US')
    assert response.status_code == 200
    assert 'Test Bank' in  [item["bankName"] for item in response.json["swiftCodes"]]
    assert 'Test Bank2' in  [item["bankName"] for item in response.json["swiftCodes"]]
    assert len(response.json["swiftCodes"])==2

def test_add_get_swift_code(client):
    response = client.post('/v1/swift-codes', json={
        "address": "456 Elm St",
        "bankName": "Another Bank",
        "countryISO2": "GB",
        "countryName": "United Kingdom",
        "isHeadquarter": True,
        "swiftCode": "ANOTHGBBXXX"
    })
    assert response.status_code == 201
    assert response.json['message'] == 'SWIFT code added successfully'
    code = SwiftCode(
        address="456 Elm St",
        bank_name="Another Bank",
        country_iso2="GB",
        country_name="United Kingdom",
        is_headquarter=True,
        swift_code="ANOTHGBBXXX"
    )

    response = client.get('/v1/swift-codes/ANOTHGBBXXX')
    assert response.status_code == 200
    assert 'Another Bank' in response.json['bankName']

def test_delete_swift_code(client):
    with app.app_context():
        code = SwiftCode(
            address="789 Pine St",
            bank_name="Delete Bank",
            country_iso2="CA",
            country_name="Canada",
            is_headquarter=False,
            swift_code="DELTCATTXXX"
        )
        db.session.add(code)
        db.session.commit()

    response = client.delete('/v1/swift-codes/DELTCATTXXX')
    assert response.status_code == 200
    assert response.json['message'] == 'SWIFT code deleted successfully'

    with app.app_context():
        deleted_code = SwiftCode.query.filter_by(swift_code="DELTCATTXXX").first()
        assert deleted_code is None

def test_get_nonexistent_swift_code(client):
    response = client.get('/v1/swift-codes/UNKNOWN123')
    assert response.status_code == 404
    assert response.json['message'] == 'SWIFT code not found'

def test_delete_nonexistent_swift_code(client):
    response = client.delete('/v1/swift-codes/FAKESCODE')
    assert response.status_code == 404
    assert response.json['message'] == 'SWIFT code not found'

def test_add_swift_code_missing_fields(client):
    response = client.post('/v1/swift-codes', json={
        # Missing required fields
        "bankName": "Incomplete Bank",
        "swiftCode": "INCOMPLETE123"
    })
    assert response.status_code == 400
    assert 'message' in response.json

def test_get_headquarter_with_branches(client):
    hq = SwiftCode(
        address="100 HQ St",
        bank_name="HQ Bank",
        country_iso2="DE",
        country_name="Germany",
        is_headquarter=True,
        swift_code="HQBNDEFFXXX"
    )
    branch = SwiftCode(
        address="101 Branch Ave",
        bank_name="HQ Bank",
        country_iso2="DE",
        country_name="Germany",
        is_headquarter=False,
        swift_code="HQBNDEFF001"
    )

    with app.app_context():
        db.session.add(hq)
        db.session.add(branch)
        db.session.commit()

    response = client.get('/v1/swift-codes/HQBNDEFFXXX')
    assert response.status_code == 200
    assert response.json['isHeadquarter'] is True
    assert len(response.json['branches']) == 1
    assert response.json['branches'][0]['swiftCode'] == "HQBNDEFF001"

def test_add_duplicate_swift_code(client):
    swift_data = {
        "address": "101 Duplicate St",
        "bankName": "Dup Bank",
        "countryISO2": "JP",
        "countryName": "Japan",
        "isHeadquarter": True,
        "swiftCode": "DUPLJPJTXXX"
    }

    client.post('/v1/swift-codes', json=swift_data)
    response = client.post('/v1/swift-codes', json=swift_data)

    assert response.status_code == 400
    assert 'SWIFT code already in the database' in response.json['message']