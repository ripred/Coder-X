from app import api_key_management as akm

def test_set_and_get_api_key():
    service = "test_service"
    key = "mysecretkey"
    akm.set_api_key(service, key)
    retrieved = akm.get_api_key(service)
    assert retrieved == key
    akm.remove_api_key(service)
    assert akm.get_api_key(service) is None
