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
   
   _Example_: IT team member who wants to initialize portions of the database,
   upgrade CC to a new version, etc.
   
1. A **translator** is a user who can create or update localization
   (translation) data.
   
   _Example_: a user wants to localize CC into a previously unsupported 
   natural language. 

## Groups Module

1. A **group admin** is user who manages the Groups module.

   _Example_: user who wants to create a new group,
   or assign a new leader to an existing group,
   or split a large group into two new, smaller groups.
   
## Courses Module

1. A **registrar** is a user who manages the data in the `courses` module.

   _Example_: Christian education pastor who wants to create a new course
   or grant a diploma.

## Events Module

1. A **scheduler** is a user who manages data in the `events` module.

   _Example_: An office worker wants to create add details for an upcoming
   retreat or schedule a worship band for the next Sunday worship service. 