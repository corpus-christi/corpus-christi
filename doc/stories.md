# Terms

1. By **application** we mean the entire _Corpus Christi_ (CC) system, including
  the user interface, API, database, administrative tools, etc.
1. CC implements a design pattern commonly called a _Single Page Application_
  (or _SPA_). To avoid terminological confusion with the previous definition of
  _application_, we refer to the SPA portion of CC as either the **user
  interface** (commonly, the **UI**) or the **web app**.
1. CC consists of several cooperating subsystems,
   each of which addresses
   a single coherent aspect of church management.
   We refer to these subsystems as **modules**.
   Initially, CC contains the following modules:

    1. `groups` - Home church/small group management and tracking
    1. `courses` - Teaching ministry management
    1. `events` - Event planning and registration

   A _module_ is intended to encompass standalone functionality
   that can optionally be used by a particular church
   in combination with any other module(s).
1. Underlying and supporting the _modules_,
   CC includes functionality we call **infrastructure**,
   which includes:
   
   1. Administrative functions (e.g., account creation)
   1. Authentication (using JSON Web Tokens)
   1. Role-based authorization 
   1. Internationalization (I18N) and Localization (L10N) 

1. Although we use the term **user** informally throughout,
   CC's data model does _not_ include a user entity.
   Instead:

   1. Any individual (human) tracked by the system we call a **Person**.
      The database includes a `Person` table.

   1. A _Person_ may be associated with an _Account_,
      which grants that _Person_ login access to CC.

   Consequently, the combination of a _Person_ and an _Account_
   can informally be considered a "user." 

# Roles

This section details the roles implemented in CC.

## Public

Portions of CC are available to completely unauthenticated users.
Strictly speaking, such a user does not have a role.
However, for convenience, we consider such users to have a **public** "role"
that permits them access to _only_ the public content of the application.

_Example_: someone browsing a list of upcoming events 
or viewing the home church map to identify a home church.

## Infrastructure

1. An **infrastructure** user is someone who can access and update
   the CC infrastructure data, including people and places.
   
   _Example_: church office worker adding a new _Account_ to the system
   or authorizing an existing account as having a particular _Role_.

1. A **superuser** is a user with essentially unlimited access to CC.
   Following are examples of things a **superuser** can do:
   - Use _all_ UI views
   - Access _all_ API endpoints
   - Modify data that is tied to application code (e.g., _Role_ data)
   - Update the CC software itself (e.g., patch defects, upgrade to new releases)
   
1. A **translator** is a user who can create or update localization
   (translation) data.
   
   _Example_: a user wants to localize CC into a previously unsupported 
   natural language. 

## Groups Module

1. A **group admin** is user who manages the Groups module.

   _Example_: user who wants to create a new group,
   or assign a new leader to an existing group,
   or add a _Person_ to an existing group,
   or split a large group into two new, smaller groups.

1. A **group leader** is in charge of a single group.

   _Example_: send a message to group members,
   or indicate that a member has attended a group meeting.

1. A **group overseer** is responsible for multiple groups.

   _Example_: send a message to members of all groups
   that the user oversees, or send a message to just the
   leaders those groups
   
## Courses Module

1. A **registrar** is a user who manages the data in the `courses` module.

   _Example_: Christian education pastor who wants to create a new course
   or grant a diploma.
   
1. A **teaching assistant** is a user who can manage course and class data
   related to _conducting classes_ (as opposed to _creating courses_,
   which is done by the **registrar**).
   
   _Example_: enter class attendance, update class meeting times,
   assign a substitute teacher for a single class.

## Events Module

1. An **event planner** is a user who manages data in the `events` module.

   _Example_: An office worker wants to create add details for an upcoming
   retreat or schedule a worship band for the next Sunday worship service. 

# CRUD Pattern 

Many stories apply one or more of the 
standard **CRUD** operations 
(_Create_, _Read_, _Update_, _Delete_)
to an entity. For example:

1. Create a new course.
1. Read the details of an existing course.
1. Update an existing course.
1. Delete an existing course.

Such verbosity would quickly become tedious.
Instead, we abbreviate CRUD operations as follows:

1. CRUD course

In some cases, we don't _delete_ data,
which can lose useful historical information.
Instead, some entities have an `active` attribute
that can be set to `false` to
_deactivate_ it.
SQL DDL that operates on such entities
must take the `active` attribute into account.
For example, when listing members of a group,
a query should return only members
whose `active` attribute is `true`.

Note that there is not necessarily a one-to-one mapping
between CRUD stories and application views.
For example,
rather than having separate views 
for the _Course_ and the _Prerequisite_ entities,
it may be much more convenient for the user 
to implement a single UI view that allows the user to work with
to _both_ the _Course_ and _Prerequisite_ entities.

# User Stories

Following are user stories for each of the roles
enumerated above.

## Infrastructure

1. Manage people known to the system
   (CRUD _Person_, _Person Attribute_).
1. Manage attributes and values that can be associated with people 
   (CRUD _Attribute_, _Attribute Value_).
1. Manage user accounts and associated roles
   (CRUD _Account_, _Account Role_).

## Superuser

Some data is tied directly to application code
(e.g., an I18N key).
Only the superuser can modify such data.

1. Update available roles (CRUD _Role_).
1. Update I18N keys (CRUD _I18N Key_). 

Furthermore, a superuser has _no restrictions_ 
on access to UI views or API endpoints.
   
## Translator

1. Add new locales (CRUD _I18N Locale_)
1. Manage localizations (CRUD _I18N Value_), including:
1. Filter localizations by key, locale, or value
1. Access a "to do" list of localizations not entered for a given locale
   and add new localizations

## Group Admin

1. Manage groups (CRUD _Group_)
1. View all groups; optionally include inactive groups
1. View members of existing groups.
1. Manage group members (CRUD _Member_, _Person_)
1. Split a large group into two new, smaller groups
1. Move a member from one group to another group
1. Manage group leader (CRUD _Group_, _Person_)
1. Manage group overseer (CRUD _Group_, _Person_)

## Group Leader

Group leaders work with exactly one group.

1. Schedule meetings (CRUD _Group Meeting_)
1. Take attendance for the current meeting (CRUD _Attendence_)
1. Update attendane for past meetings (CRUD _Attendance_)
1. List group meetings (past and scheduled).
1. List group members.
1. View member attendance report.
1. Send an email message to one, more than one, or all group members.

## Group Overseer

Group overseers work with more than one group.
By _all_, we mean only the members/leaders/groups 
that this user oversees.

1. View a list of active/inactive groups.
1. View a list of active/inactive groups and their active/inactive members.
1. Send an email message to one, more than one, or all group _leaders_.
1. Send an email message to all _members_ of one, more than one, or all groups.

## Registrar

1. Manage courses (CRUD _Course_, _Prerequisite_)
1. Manage course offerings (CRUD _Course Offering_)
1. Manage diplomas (CRUD _Diploma_, _Diploma Course_)
1. Award diplomas (CRUD _Diploma Awarded_)

## Teaching Assistant

1. Confirm self-registered students
1. Schedule meetings (CRUD _Class Meeting_)
1. Arrange teachers for class meetings (CRUD _Class Meeting_, _Person_)
1. Take attendance (CRUD _Class Attendance_)

## Event Planner

1. Manage events (CRUD _Event_)
1. Manage event assets (CRUD _Asset_, _Event Asset_)
1. Manage event teams (CRUD _Team_, _Team Member_, _Event Team_, _Person_)
1. Manage event individuals (CRUD _Event Person_, _Person_)

## Event Assistant

1. Confirm self-registered participants (CRUD _Event Participant_, _Person_)
