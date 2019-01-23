import pytest

def flip():
    """Return true or false randomly."""
    return random.choice((True, False))

# ---- Group

@pytest.mark.smoke
def test_download_image(auth_client):
    # GIVEN some randomly created images
    # WHEN
    # THEN
    assert True == False

@pytest.mark.smoke
def test_upload_image(auth_client):
    # GIVEN some randomly created images
    # WHEN
    # THEN
    assert True == False

@pytest.mark.smoke
def test_update_image(auth_client):
    # GIVEN some randomly created images
    # WHEN
    # THEN
    assert True == False

@pytest.mark.smoke
def test_delete_image(auth_client):
    # GIVEN some randomly created images
    # WHEN
    # THEN
    assert True == False