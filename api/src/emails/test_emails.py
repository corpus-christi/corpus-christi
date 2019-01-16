@pytest.mark.smoke
def test_send_email(auth_client):
    # GIVEN nothing

    # WHEN we try to send an email
    resp = auth_client.post(url_for('emails.send_email'), json = email_object_factory())

    # THEN we expect the correct code
    assert resp.status_code == 200


@pytest.mark.smoke
def test_send_email_invalid(auth_client):
    # GIVEN nothing

    # WHEN we try to send an invalid email
    email = email_object_factory()
    email[fake.word()] = fake.word()
    resp = auth_client.post(url_for('emails.send_email'), json = email)

    # THEN we expect an error code
    assert resp.status_code == 422

