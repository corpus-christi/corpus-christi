# Coding Guidelines

Observe these guidelines **in addition**
to the guidelines specified in the GitHub Wiki.

## RESTful API

CC's API strives to be RESTful. 
Observe these conventions
and update them to reflect
actual practice in the code.
Include examples.

### General

1. Resources named in endpoints should be _plural_
   (Use `/groups` not `/group`).
2. Flask routes should always include the `method` argument,
   even if it is the default. For example:
   ```python
   @groups.route('/groups', methods=['GET'])
   ```
3. Refer to a single instance of a resource
   using its ID (which is also usually its primary key)
   ```
   /groups/42
   ```

### Create

1. Create a new instance of a resource.
   * Method: `POST`
   * Payload: all required attributes of new resource
     and any optional attributes as appropriate
   * Example: `/groups`

### Retrieve

1. Retrieve all instances of a resources.
   * Method: `GET`
   * Payload: None
   * Example: `/groups`
2. Retrieve one instance of a resource by ID (primary key);
   the ID should be part of the URL.
   * Method: `GET`
   * Payload: None
   * Example: `/groups/42`

When fetching a collection of resources,
the API supports
paging (retrieving a subset of the resources),
searching by attribute value,
and sorting of the returned resources.
Use URL query strings
to supply parameters 
for paging, searching, and sorting.

Note that these query string parameters
may be used in flexible combinations 
(e.g., search for resources with a particular
attribute value and return a limited number
of those resources beginning at a specific offset).

#### Paging

To request a subset of a large collection of resources,
use `offset` and `limit` in the URL query string.

1. Retrieve values starting at a given offset
   * Example: `/groups?offset=20` returns groups resources
     starting with the 20th group
1. Limit the number of resources returned
   * Example: `/groups?limit=50` limits the number of resources
     returned to no more than 50
1. The `offset` and `limit` parameters may be used together
   * Example: `/groups?offset=20&limit=50` retrives
     no more than 50 groups starting with the 20th group

#### Searching

To retrieve resources with specific values for attributes,
use `where` in the URL query string.

1. Retrieve resources with a single matching attribute.
   * Example: `/groups?where=active:true`
     retrieves all active groups
1. Retrieve resources matching multiple attributes.
   * Example: `/groups?where=active:true&where=name:Adult`
     retrieves active groups with `Adult` in their name

#### Sorting

To sort results
use `order` in the URL query string.

1. Order by a single attribute
   * Example: `/groups?order=name:asc` 
     retrieves all groups ordered ascending by name
1. Order by multiple attributes.
   * Example: `/people?order=last_name:asc&order=first_name:desc`
     retrieves all people, ordered ascending by last name,
     then descending by first name.

### Update

In general, `PATCH` requets will be 
much more common than `PUT` requests.

1. Change selected attributes of a single resource by ID;
   the ID should be part of the URL.
   * Method: `PATCH`
   * Payload: only attributes being updated
   * Example: `/groups/42`
2. Replace an existing resource in its entirity;
   the ID of the resource should be part of the URL.
   * Method: `PUT`
   * Payload: all required attributes of new resource
     and any optional attributes as appropriate
   * Example: `/groups/42`


### Delete

Only _rarely_ should we actuall delete application data.
Instead,
a resource should have an `active` attribute
that defaults to be `TRUE`,
and is set to `FALSE` when the resource is "deleted."

1. Deactivate a selected resource by ID;
   the ID should be part of the URL.
   * Method: `DELETE`
   * Payload: None
   * Example: `/groups/42`

## Vue Files

1. Put comments in the `<template>` section
   of your Vue files.
   Use an ordinary HTML comment:
   ```html
   <!-- Comment -->
   ``` 
   Happily, these will be stripped out
   when rendering the template.