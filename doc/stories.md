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

## Visitor

Portions of CC are available to completely unauthenticated users.
Strictly speaking, such a user does not have a role.
However, for convenience, we consider such users to have a **visitor** "role"
that permits them access to _only_ the public content of the application.

A **visitor** cannot enroll in courses, sign up for events, etc.
without first registering with CC and thereby becoming a **public user**.

_Example_: someone browsing a list of upcoming events 
or viewing the home church map to identify a home church.

## Public

A **visitor** can register for an account on the system,
promoting the visitor to a **public** user.
When registering as a **public** user,
a church attendee submits personal data just once,
simplifying course registration and event sign up in the future.
Registration creates a _Person_ instance and an _Account_
instance for the user.

During registration, a **public** user provides a username and password
that are stored in the _Account_ entity and are used later
when the user wants to interact with the system.

For example, 
if a public user clicks through a link to register for an _Event_,
he or she is prompted to enter their username and password,
which is used to look up their _Person_ data and 
complete the registration or sign-up.

It is also possible for a **visitor** to click on a link
for an _Event_ or _Course_.
Consequently, the page that requests username and password
should also include a link to the page where a visitor
can sign up to become a **public** user.

### Public User Validation

Data entered during **public** user registration
is considered **unconfirmed**
and must be validated by an authorized CC account holder.
The goal of this process is to vet data entering the system, 
eliminate duplicate data, and generally avoid unquality.

For example:
1. A **visitor** registers to become a **public** user.
1. CC creates an unconfirmed _Person_ and associated _Account_ instance.
1. A CC user with the **infrastructure** role inspects the unconfirmed _Person_ instance.
   The user may:
   1. Reject the _Person_ instance, deleting it and the associated _Account_ from the database.
      For example, an empty, incomplete, or obviously bogus entry can simply be removed
      (actually _deleted_, not just marked inactive).
   1. Search for an existing _Person_ instance that matches this public user
      (e.g., from a previous registration).
      CC provides tools to identify an existing _Person_ instance (e.g., live search).
      - If _no_ existing _Person_ is found,
        and the data submitted by the would-be **public** user is valid, 
        the **infrastructure** user
        marks the _Person_ record as `confirmed`.
      - If an existing _Person_ _is_ found, the **infrastructure** user
        reconciles the existing and new _Person_ instances into a single _Person_
        instance (e.g., updating the older _Person_ with new data)
        and marks the resulting _Person_ record as confirmed.
        It should be easy for the **infrastructure** user to 
        to see both the existing and new _Person_ details
        and to choose the version that will "survive"
        into the single, final _Person_ record.

### Self Registration

A **public** user may self register for:
- A _Course Offering_
- An _Event_
The **public** user clicks on the offering or event
then supplies his or her username and password.
The system validates these login credentials
and, if valid, adds the corresponding _Person_
to the _Event_, _Course Offering_, etc.



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

# User Stories

Following are user stories for each of the roles
enumerated above.

## Visitor

1. A **visitor** should be able to create an _Account_ and the associated _Person_,
   "promoting" the **visitor** to a **public** user.
   This will allow a church attendee to enter personal data just once
   and reuse it in the future without reentering it.

   When a **visitor* creates an account,
   be generous with the the `username`.
   There must be one, but it:
   - must be unique across all _Account_'s
   - can be an email address
   - can be a phone number
   - can be a tax ID number (common identifier in Ecuador)
   - can be an arbitrary string (user may not have an email address or username)
   
   Require a password with a minimum length of 8 characters
   with at least one letter and one number.

## Public

1. Update existing _Person_ or _Account_ data.

1. Authenticate with an existing _Account_
   by providing a valid username and password
   (e.g., when signing up for an _Event_). 
   Follow this procedure:
   1. If there is an _Account_ with the username,
      try to validate with the _Account_ and its hashed_password.
   1. If that fails,
      search for a _Person_ with a phone number matching what the user entered as a username;
      if such a _Person_ record exists and has an associated _Account_,
      try validating with the phone number as the username and the hashed password
      of the associated _Account_
   1. If that fails,
      search for a _Person_ with an email address matching what the user entered as a username;
      if such a _Person_ record exists and has an associated _Account_,
      try validating with the email address as the username and the hashed password
      of the associated _Account_
   1. If that fails,
      offer the user the option of
      - entering an email address to receive a password reset link
      - creating a new _Account_ and _Person_ (as above)
      If the email address doesn't exist in the _Person_ entity,
      inform the user of that fact and allow them to enter a different one.
      If the email address does exist,
      indicate that the user should check for a new email to that address.
      
      The email sent to a known email address should include a password reset link.
      The link should contain:
      - A URL for the CC password reset page
      - A freshly generated token (e.g., a SHA1 hash of the current date/time)
        that is stored in the _Account_ table with the email address.

      In addition, an expiration timestamp should be stored in the _Account_ entity,
      set for four hours in the future.

1. Handle a password reset email.
   Upon clicking the link:
   - If the link contains a valid, unexpired password reset token, the user should
     be directed to a page on which the password for the account matching
     the token may be changed (enter password, repeat)
   - If the link contains a nonexistent password reset token, the user should
     be directed to a page indicating that the link is invalid.
   - If the link contains a valid password token with an expired timestamp,
     the user should be informed that they waited to long to reset the password
     and be given the opportunity to start over by submitting their email address.
   If a token is found (whether expired or not),
   it and the associated expiration timestamp should be deleted from the
   the _Account_ entity. 

## Infrastructure

In this section, the term _people_ means
one or more instances of the _Person_ entity.

### People

1. Add a new _Person_, including all active _Person Attributes_.
   It should be easy to add multiple people.
1. Update an existing _Person_ and associated _Person Attributes_.
1. Deactivate or reactivate a _Person_.
1. List all _people_
1. Search for _people_ using query-by-example (QBE) 
   on first name, last name, phone, email, or active status.
1. List _people_ matching search criteria (including all _people_)
1. Prepare a printable report of _people_ matching search criteria (including all _people_)
1. Export _people_ matching search criteria (including all _people_) to a comma-separated value file
   suitable for import into a spreadsheet (Excel, Numbers, Google Sheets).
   
### Accounts and Roles

1. Add a new _Account_ for an existing _Person_.
1. Add a new _Account_ as well as the _Person_ who will be associated with that _Account_.
1. Change an _Account_'s username or password.
1. Deactivate or reactivate an _Account_.
1. Add or remove an association between an _Acocunt_ and a _Role_.
1. List all roles. Optionally include the username and first and last names of _Account_'s that
   have that role.
1. Search for an _Account_ by username or by the _Person_ associated with the _Account_
   using the same QBE criteria as for _people_.
1. List accounts matching _Account_ search criteria,
   including username, first and last name of the associated _Person_, and names of associated _Role_'s.
   Such a list should allow the user to navigate to the associated _Person_ or _Role_'s.

### Person Attributes

1. Define a new string-valued _Person Attribute_; available types
   should include `Date`, `Integer`, `Short Answer`
1. Define a new enumerated _Person Attribute_ including _Enumerated Value_ instances
   for the new attribute.
1. Add a new _Enumerated Value_ for an existing enumerated attribute.
1. Deactivate or reactivate an _Enumerated Value_   
1. Deactivate or reactivate a _Person Attribute_.
1. Rename a person attribute.
1. Rename an _Enumerated Value_.

### Managers

1. Add a _Person_ as a _Manager_ with the appropriate `description`;
   Valid `description`'s are determined by the module for which a manager is being defined
   (e.g., "Group Leader" or "Group Overseer" for the Groups module.)
   Allow an existing _Manager_ to be associated with the new _Manager_ as it is being added.
1. Add a new _Manager_ for a _Manager_.
1. Update the _Manager_ of an existing _Manager_.
1. Show the hierarchy of _Manager_'s as a tree structure. Clicking on any node in the tree
   should allow the selected _Manager_ to be updated.
1. Replace the _Person_ associated with a _Manager_ (e.g., when a different _Person_ is taking
   over as the leader of a group).
   
### Places

1. Create a new _Address_ with a valid street address.
   The user should be able to specify the _Area_ in the following ways:
   - Choose an existing _Area_ using live search.
   - Add a new _Area_ in the same view and associate it with the _Address_.
   The `latitude` and `longitude` may be specified in the following ways:
   - Enter the values directly
   - Use integrated Google Maps geolocation to look up the address and 
     store the resulting latitude and longitude in the instance.
1. Create a new _Address_ without a street address.
   The user should be able to specify the _Area_ in the following ways:
   - Choose an existing _Area_ using live search.
   - Add a new _Area_ in the same view and associate it with the _Address_.
   The `latitude` and `longitude` must be specified in one of the following ways:
   - Enter the values directly
   - Use integrated Google Maps to pinpoint a location and 
     store the resulting latitude and longitude in the instance.
1. Update an existing _Address_ using the methods detailed above.
1. Create a new _Area_.
1. Update an existing _Area_.
1. Create a new _Location_ for an existing _Address_.
1. Update an existing _Location_.
1. List all _Address_'s; allow live filtering by:
   - `name`, `address`, `city`, _Area_, _Country_,
   - range of both `latitude` and `longitude` values,
   - specified distance from a specific `latitude` and `longitude`.
   - specified distance from a selected _Address_.
1. Show locations on an integrated Google Map,
   using the same filters available for the list of _Addresses_.
1. Show _Location_'s for an _Address_ that is selected by live search.

## Superuser

A superuser has _no restrictions_ 
on access to UI views or API endpoints.

Some data are tied directly to application code
(e.g., a _Role_ or an _I18N key_).
_Only_ a superuser can modify such data.

### Roles

1. Add a new _Role_.
1. Update the name of an existing role.
1. Deactivate or reactivate a role.

### Attributes

1. Add a new _Attribute_ type.

### I18N

1. Add a new _I18N Key_.
1. Change an existing _I18N Key_.

## Translator

1. Update the `description` of an existing _I18N Key_.
1. Add a new _I18N Locale_.
1. Update the `description` of an existing _I18N Locale_.
1. (Localization Status) List all _I18N_Locale_ instances;
   for each locale, 
   include the number of _I18N Value_'s that have been created for that locale
   and the percentage of all _I18N Key_'s that have been localized.
1. (Localization Workbench) List all localizations, including
   _I18N Key_ `id` and `description`,
   _I18N Locale_ `code`,
   and
   _I18N Value_ `gloss`.
   Allow the user to live filter by `id`, `code`, `gloss`, entries without a gloss, or `verified`.
   Regardless of the active filter,
   the user should be able to update or add any visible `gloss`.
   and set `verified` flag when checked by a native language speaker.
   Allow the user to display one or more _existing_ glosses for other locales.
1. Integrate Google Translate into the Localization Workbench:
   allow the user to request a gloss from Google
   based on any existing gloss (from another locale) into the target locale.

## Group Admin

1. Add a new _Group_. As part of the process:
   - Allow an existing _Person_ to be designated a _Manager_ with `description` "Group leader".
   - Allow new _Person_ to be created as the _Manager_ of the group.
1. Update the name, description, and leader of an existing _Group_.
1. Assign a _Manager_ (and associated _Person_) as the "Group leader".
1. Set the "Group overseer" _Manager_ for this _Group_.
1. Deactivate and reactivate a _Group_.     
1. Add _Person_'s as _Group Member_'s of an existing group.
   It should be easy to add multiple _Group Member_ instances.
   New _Group Member_'s may be:
   - An existing _Person_ who should be easy to find using filtering
   - A new _Person_ whose details should be easy to enter as part of adding the _Person_ 
     as a _Group Member_ of the _Group_.
1. Deactivate and reactivate a _Person_ as a _Group Member_ of the _Group_.
1. Split a large group into two new, smaller groups.
   Create the two new _Group_'s (as detailed above)
   and choose the destination _Group_ for each of the members
   of the existing group.
   Deactivate the old group.
1. Move a _Group Member_ from one _Group_ to another existing _Group_.
1. List all groups, including group leader's name and number of members.
   Optionally, include inactive groups.
1. View report of group attendance (group name vs meeting date)
1. View line graph of group attendance (attendees vs date).
   One line per group, allow groups to be filtered by name
   (e.g., check box per group).
   Allow time scale to be changed (e.g., weekly, monthly, annually).
   Allow time range to be changed (e.g., year-to-date, past 12 months, specific dates, all time)
   
## Group Leader

Group leaders work with exactly one group.

1. Schedule a _Meeting_ (create a _Meeting_ instance).
   Allow the meeting location to be chosen in the following ways:
   - An existing _Location_ using a live search
   - A past _Meeting_ location (e.g., from a drop-down list)
   - A new location, which should be easy to enter on the same page.
1. Update any of the above details of a previously scheduled (but not yet held) _Meeting_.
1. Take attendance for the current meeting
   by adding or removing instances of _Group Attendance_.
1. List group meetings (past and scheduled).
1. List group members.
1. View report of member attendance (member name vs. meeting dates)
1. View line graph of number of attendees by meeting date.
1. Send an email message to one, more than one, or all group members.

## Group Overseer

Group overseers work with more than one group.
By _all_, we mean only the members/leaders/groups 
that this user oversees.

1. List all groups, including group leader's name and number of members.
   Optionally, include inactive groups.
1. List members by group.
   Optionally include inactive groups. 
   Optionally include inactive members.
1. View report of group attendance (group name vs meeting date)
1. View line graph of group attendance (attendees vs date).
   One line per group, allow groups to be filtered by name
   (e.g., check box per group).
   Allow time scale to be changed (e.g., weekly, monthly, annually).
   Allow time range to be changed (e.g., year-to-date, past 12 months, specific dates, all time)
1. Send an email message to one, more than one, or all group _leaders_.
1. Send an email message to all _members_ of one, more than one, or all groups.

## Registrar

### Courses

1. Create a new _Course_, including course _Prerequisites_.
   If a _Prerequisite_ doesn't yet exist, it should be easy to add that course
   and associated it as  _Prerequisite_.
1. Update the details of a _Course_, including _Prerequisite_'s.
1. Deactivate or reactivate a _Course_.

### Course Offerings

1. Create a _Course Offering_ for an existing _Course_.
1. Update the details of an existing _Course Offering_.
1. Deactivate or reactivate a _Course Offering_.

### Diplomas

1. Create a _Diploma_ and associate the _Courses_ necessary 
   to earn the _Diploma_.
1. Update the details of an existing _Diploma_,
   including the required _Course_'s.
1. Deactivate or reactivate a _Diploma_.
1. Award a _Diploma_ to a _Student_.
1. Display a transcript for each _Student_, showing course and diploma information for that _Student_.

## Teaching Assistant

### Students

1. Confirm self-registered students
1. Manually enter students.
   Allow the student to be chosen in the following ways:
   - An existing _Person_, using live search.
   - A _Person_ who has taken any _Course_ before.
   - A new _Person_, whose details should be easy to enter
     in the context of adding a student to a _Course Offering_.
1. Enter or update _Class Attendance_ for a _Class Meeting_.

### Class Meetings

1. Schedule _Class Meetings_ for existing _Course Offering_'s.
   Allow the meeting location to be chosen in the following ways:
   - An existing _Location_ using a live search
   - A past _Class Meeting_ location (e.g., from a drop-down list)
   - A new location, which should be easy to enter on the same page.
1. Set the teacher for a _Class Meeting_.
   Allow the teacher to be chosen in the following ways:
   - An existing _Person_, using live search.
   - A _Person_ who has taught this same course in the past (e.g., from a drop-down list)
   - A _Person_ who has taught _any_ course
   - A new _Person_, whose details should be easy to enter
     in the context of assigning a teacher to a _Class Meeeting_.
1. Update existing _Class Meetings_ scheduled in the future;
   the same filtering/selection capabilities just described
   should be available when updating _Class Meeting_'s.

## Event Planner

### Events

1. Create a new _Event_.
   Allow the event location to be chosen in the following ways:
   - An existing _Location_ using a live search
   - A past _Event_ location.
   - A new location, which should be easy to enter on the same page
     on which the _Event_ is created.
1. Update an existing _Event_; provide functionality similar
   to creating an _Event_.
1. Deactivate ("cancel") or reactivate an event.
1. Duplicate an _Event_ (e.g., Sunday service).
   Take the user to a view where the details
   of the copy can be updated.
   Ensure the copy doesn't overlap the original temporally.
1. List _Event_'s by date. Show the _Event_ `title`
   and the `start` and `end` dates/times.
   Allow the user to specify the date range,
   including: past 12 months, past 3 months, past month,
   this month, next 3 months, next year,
   arbitrary date range.
1. Show _Event_'s in a calendar view;
   allow the same date ranges as for the list view.
1. Selectively export _Event_'s to Google Calendar.

### Assets

1. Add a new _Asset_. Allow the location to be set using the 
   same criteria as for creating an _Event_.
1. Update the details for an _Asset_.
1. Deactivate or reactivate an _Asset_ (an inactive _Asset_ is
   no longer available for future _Event_'s)
1. Associate an _Asset_ with an _Event_
   (add or remove _Event Asset_ instance).
   Ensure that assets are not double-booked.
1. List all available assets,
   including the number of events in which they have been used.
   Allow filtering by description (partial match) or location.

### Teams
   
1. Add a new _Team_.
1. Update an existing _Team_.
1. Deactivate or reactivate a _Team_.
1. Associate _Person_'s with a _Team_
   (add or remove _Team Member_ instance)
   Allow the _Person_ to be chosen in the following ways:
   - An existing _Person_, using live search.
   - A new _Person_, whose details should be easy to enter
     in the context of assigning a _Team Member_.
1. Associate a _Team_ with an _Event_
   (add or remove an _Event Team_ instance).
   Ensure that a team is not double booked.
1. List all teams, including `description` and full name of each _Team Member_.
   Optionally include inactive teams.
1. List all _Person_'s who have been a team member in the past.
   Include the team(s) of which they have been part.

### Individuals

1. Add a new _Event Person_ (e.g., keynote speaker)    
   Allow the _Person_ to be chosen in the following ways:
   - An existing _Person_, using live search.
   - A new _Person_, whose details should be easy to enter
     in the context of assigning an _Event Person_.
   Ensure that an _Person_ is not double-booked.
1. Update an _Event Person_; provide the same capabilities
   as when creating a new _Event Person_.
1. List all _Event Persons_ associated with an _Event_.

## Event Assistant

1. Confirm self-registered participants.
1. Manually enter participants.
   Allow a participant to be chosen in the following ways:
   - An existing _Person_, using live search.
   - A new _Person_, whose details should be easy to enter
     in the context of adding a participant.
1. Send an email to all confirmed _Event Participants_ with a known email address
   (e.g., news about the event).
1. Send an email message to all members of a selected _Team_.
1. Send an email to one or more _Event Person_'s
   (choose from checkbox list).
1. Send an email message to every _Event Team_ member and _Event Person_.
