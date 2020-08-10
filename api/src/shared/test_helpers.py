from .helpers import list_to_tree


def test_list_to_tree():
    # GIVEN a normal valid list
    normal_list = [
        {'path': 'alt.logo', 'value': 'Alt text for logo'},
        {'path': 'app.name', 'value': 'Application name'},
        {'path': 'app.desc', 'value': 'This is a test application'},
        {'path': 'courses.name', 'value': 'Name of the courses module'},
        {'path': 'courses.date.start', 'value': 'Start date of course'},
        {'path': 'courses.date.end', 'value': 'End date of course'},
        {'path': 'btn.ok', 'value': 'Label on an OK button'},
        {'path': 'btn.cancel', 'value': 'Label on a Cancel button'},
        {'path': 'label.name.first', 'value': 'Label for a first name prompt'},
        {'path': 'label.name.last', 'value': 'Label for a last name prompt'}
    ]
    # WHEN we try to convert it to a tree
    try:
        list_to_tree(normal_list)
    # THEN we expect no error to occur
    except RuntimeError:
        assert False

    # WHEN we add a bogus entry in the list
    normal_list.append({'path': 'btn.cancel.bogus', 'value': 'bogus value'})
    # THEN we expect the conversion to raise an error
    try:
        list_to_tree(normal_list)
        assert False
    except RuntimeError as e:
        assert True
