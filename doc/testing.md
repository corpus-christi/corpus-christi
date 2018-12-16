# Testing

This document details our testing standards.

## API Testing

API testing uses these packages:
- [`pytest`](https://docs.pytest.org/en/latest/index.html) - test framework
- [`pytest-cov`](https://pytest-cov.readthedocs.io/en/latest/) - coverage testing

Each component of the API has its own dedicate test file(s).
Here is an example from `i18n`.
```python
@pytest.mark.parametrize('id, desc', locale_tuples)
def test_delete_one_locale(client, dbs, id, desc):
    # GIVEN locales from static data
    create_locales(dbs)

    # WHEN one locale deleted
    resp = client.delete(url_for('i18n.delete_one_locale', locale_id=id))

    # THEN result is "No content"
    assert resp.status_code == 204

    # AND the deleted locale doesn't exist in the database.
    result = I18NLocale().query.all()
    assert len(result) == len(locale_tuples) - 1
    for loc in result:
        assert loc.id != id
        assert loc.desc != desc
```
Things to note as patterns for new tests:
- Name the test "`test_` _something-close-to-name-of-endpoint_"
- Parmetrize tests as approrpriate to broaden test coverage
- Use the [`GIVEN-WHEN-THEN`](https://martinfowler.com/bliki/GivenWhenThen.html)
  framework for documenting tests.
- Always test status codes and returned content
- Do as many `assert` calls as necessary to check all possible outcomes.
- Use the ORM to set up or verify the contents of the database as required.
- Don't hardwire URLs into tests;
  use the `url_for` function,
  which takes the name of the **view function**
  that implements the endpoint under test.

### Fixtures

The `pytest` package uses _fixtures_ to share common
data among tests.
Most fixtures are defined in the `conftest.py` file
and include:
1. `app` is the top-level Flask application object
1. `client` is the Flask test client;
   this is the object to use to make requests to the API. 
1. `orm` is the object-relational mapper (SQLAlchemy)
1. `dbs` is a database "session" object for SQL alchemy;
   use this to execute database operations
   via SQLAlchemy models.
To access a fixture from within a test,
simply name it in the test function's argument list.
The `pytest` framework will inject the fixture,
making it available to your test.

### Status Codes

The API should use these status codes; **check** for them.

- `200` - `Ok`: everything worked and there is no more specific status code
- `201` - `Created`: a new resources was _created_ successfully.
- `204` - `No content`: confirm that a resource has been _deleted_
- `400` - `Bad request`: something was wrong with the request,
  and we couldn't give back more information;
  the error status of last resort
- `404` - `Not found`: the resource couldn't be located
- `422` - `Unprocessable entity`: the request failed validation
- `500` - `Internal server error`: something on the server went horribly wrong.
  In general, API code should _not_ return this;
  it normally comes from the system or framework.

## UI Testing

TODO